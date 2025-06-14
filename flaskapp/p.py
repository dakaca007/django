import requests
from datetime import datetime, timedelta
import os
import time
import json
import random
from bs4 import BeautifulSoup, SoupStrainer
import concurrent.futures
from functools import lru_cache
import threading
import queue
import tempfile
import shutil
import math

# 配置项
START_ID = 1
END_ID = 2060020
INITIAL_DATE_RANGE = (datetime(2010, 1, 1), datetime(2025, 12, 31))  # 初始日期搜索范围
PROGRESS_JSON = "progress.json"
FAILED_FILE = "failed.txt"
SONGS_META_FILE = "songs_meta.json"
BATCH_SIZE = 20
MAX_WORKERS = 5
MAX_RETRIES = 3
MAX_DATE_SHIFT = 14  # 扩大日期偏移范围
AUTO_DETECT_SAMPLES = 10  # 自动探测时测试的样本数

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
session = requests.Session()
session.headers.update(HEADERS)

# 线程安全的队列，存放待写入的元数据
meta_queue = queue.Queue()

def load_progress():
    if os.path.exists(PROGRESS_JSON):
        try:
            with open(PROGRESS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            sid = int(data.get("song_id", START_ID))
            ldate = datetime.fromisoformat(data.get("last_date", INITIAL_DATE_RANGE[0].isoformat()))
            return sid, ldate
        except Exception:
            print("⚠️ 进度文件损坏，重置进度")
    return None, None  # 返回None表示需要自动探测

def save_progress(song_id, last_date):
    try:
        with open(PROGRESS_JSON, "w", encoding="utf-8") as f:
            json.dump({
                "song_id": song_id,
                "last_date": last_date.date().isoformat()
            }, f)
    except Exception as e:
        print(f"❌ 保存进度失败: {e}")

def auto_detect_start_params():
    """自动探测有效的起始ID和日期"""
    print("🔍 开始自动探测有效的起始参数...")
    
    def test_params(song_id, test_date):
        """测试单个参数组合"""
        mp3_url, _ = find_mp3_url(song_id, test_date)
        return mp3_url is not None
    
    # 在ID范围内随机选择样本
    test_ids = random.sample(range(START_ID, END_ID), min(AUTO_DETECT_SAMPLES, END_ID-START_ID))
    
    # 在日期范围内生成候选日期
    date_range = (INITIAL_DATE_RANGE[1] - INITIAL_DATE_RANGE[0]).days
    test_dates = [INITIAL_DATE_RANGE[0] + timedelta(days=random.randint(0, date_range)) 
                 for _ in range(AUTO_DETECT_SAMPLES)]
    
    # 并行测试所有组合
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for song_id in test_ids:
            for test_date in test_dates:
                futures.append(executor.submit(test_params, song_id, test_date))
        
        # 等待第一个成功的结果
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                song_id = futures[0].args[0]  # 获取成功的song_id
                test_date = futures[0].args[1]  # 获取成功的test_date
                print(f"✅ 探测到有效参数 - ID: {song_id}, 日期: {test_date.date()}")
                return song_id, test_date
    
    # 如果没有找到，使用默认值并扩大日期范围
    print("⚠️ 自动探测失败，使用默认参数")
    return START_ID, INITIAL_DATE_RANGE[0]

def find_mp3_url(song_id, base_date):
    """改进的MP3查找函数，支持动态日期范围"""
    base = "https://music.jsbaidu.com/upload/128"
    
    # 动态调整日期范围，基于song_id的哈希值引入一些随机性
    date_shift = MAX_DATE_SHIFT + (song_id % 7)  # 在MAX_DATE_SHIFT基础上增加0-6天
    
    # 生成日期序列，包括向前和向后搜索
    dates = [base_date + timedelta(days=i) for i in range(-date_shift//2, date_shift//2 + 1)]
    random.shuffle(dates)  # 随机化搜索顺序
    
    with concurrent.futures.ThreadPoolExecutor() as ex:
        futures = {
            ex.submit(url_exists, f"{base}/{d:%Y/%m/%d}/{song_id}.mp3"): d
            for d in dates
        }
        for fut in concurrent.futures.as_completed(futures):
            url = fut.result()
            if url:
                print(f"🎯 找到 MP3（ID:{song_id} 日期:{futures[fut].date()}）")
                return url, futures[fut]
    
    print(f"🚫 未找到 MP3（ID:{song_id}）")
    return None, base_date + timedelta(days=1)  # 没找到时日期+1天

def process_batch(batch_ids, cur_date):
    """改进的批处理函数，包含智能回溯"""
    success_count = 0
    last_success_date = cur_date
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(process_one, sid, cur_date) for sid in batch_ids]
        for fut in concurrent.futures.as_completed(futures):
            sid, nd = fut.result()
            if nd:  # 如果成功找到MP3
                success_count += 1
                last_success_date = nd
            else:
                # 失败时尝试调整日期
                if success_count > 0:
                    # 如果有成功记录，保持当前日期
                    pass
                else:
                    # 连续失败，调整日期
                    days_to_add = random.randint(1, 3)
                    last_success_date += timedelta(days=days_to_add)
                    print(f"🔄 调整日期 +{days_to_add}天 由于连续失败")
    
    # 根据成功率动态调整日期
    success_rate = success_count / len(batch_ids)
    if success_rate < 0.3:  # 如果成功率低于30%
        days_to_add = math.ceil((0.5 - success_rate) * 5)  # 动态计算要增加的天数
        last_success_date += timedelta(days=days_to_add)
        print(f"📈 低成功率({success_rate:.0%})，调整日期 +{days_to_add}天")
    
    return last_success_date

def main():
    # 加载进度或自动探测
    sid, cdate = load_progress()
    if sid is None or cdate is None:
        sid, cdate = auto_detect_start_params()
    
    print(f"🚀 开始采集，起始 ID: {sid}, 起始日期: {cdate.date()}")

    stop_event = threading.Event()
    writer = threading.Thread(target=meta_writer_thread, args=(stop_event,), daemon=True)
    writer.start()

    try:
        consecutive_failures = 0
        while sid < END_ID:
            end = min(sid + BATCH_SIZE, END_ID)
            print(f"\n🔄 批次采集 ID {sid}–{end - 1}")
            
            cdate = process_batch(range(sid, end), cdate)
            save_progress(end, cdate)
            sid = end
            
            # 动态等待时间，基于连续失败次数
            if consecutive_failures > 3:
                wait_time = random.uniform(2, 5)
                print(f"⚠️ 连续失败{consecutive_failures}次，延长等待时间至{wait_time:.1f}s")
            else:
                wait_time = random.uniform(0.5, 1.5)
            print(f"⏳ 等待 {wait_time:.1f}s 继续")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n🛑 用户中断，保存进度...")
    except Exception as e:
        print(f"❌ 程序异常退出: {e}")
    finally:
        print("🛑 等待队列写完数据")
        meta_queue.join()
        stop_event.set()
        writer.join()
        session.close()
        print("🎉 采集任务结束")

if __name__ == "__main__":
    main()
