# crawler.py
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import concurrent.futures
import time
import random
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置
START_ID = 861573
END_ID = 861600  # 测试范围，成功后改为960020
INITIAL_DATE = datetime(2017, 5, 11)
MAX_DATE_SHIFT = 14
BATCH_SIZE = 10  # 小批量测试
MAX_WORKERS = 3  # 低并发测试

SONGS_JSON = "songs_meta.json"
FAILED_FILE = "failed_songs.txt"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
]

def ensure_directories():
    """确保必要的目录存在"""
    for path in [SONGS_JSON, FAILED_FILE]:
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

def load_songs():
    """安全加载已有歌曲数据"""
    try:
        if os.path.exists(SONGS_JSON):
            with open(SONGS_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"加载歌曲数据失败: {e}")
        return []

def save_songs(songs):
    """保存歌曲数据到文件"""
    try:
        with open(SONGS_JSON, "w", encoding="utf-8") as f:
            json.dump(songs, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 成功保存 {len(songs)} 首歌曲数据")
        return True
    except IOError as e:
        logger.error(f"保存歌曲数据失败: {e}")
        return False

def log_failed(song_id, reason=""):
    """记录失败的歌曲ID"""
    try:
        with open(FAILED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{song_id}: {reason}\n")
        logger.warning(f"记录失败ID: {song_id} - {reason}")
    except IOError as e:
        logger.error(f"记录失败ID失败: {e}")

def find_mp3_url(song_id, base_date):
    """查找有效的MP3文件URL"""
    # 修复URL协议 (添加冒号)
    base = "https://music.jsbaidu.com/upload/128"
    
    # 双向日期搜索 (前7天后7天)
    date_range = range(-MAX_DATE_SHIFT//2, MAX_DATE_SHIFT//2 + 1)
    dates = [base_date + timedelta(days=i) for i in date_range]
    
    for d in dates:
        url = f"{base}/{d.strftime('%Y/%m/%d')}/{song_id}.mp3"
        try:
            # 使用GET请求+流式传输
            with requests.get(
                url, 
                timeout=8,
                headers={'User-Agent': random.choice(USER_AGENTS)},
                stream=True
            ) as r:
                # 关键验证点
                if r.status_code == 200:
                    content_type = r.headers.get('Content-Type', '').lower()
                    content_length = int(r.headers.get('Content-Length', 0))
                    
                    # 验证音频文件和合理大小
                    if ('audio' in content_type or 'mpeg' in content_type) and 1024 < content_length < 10*1024*1024:
                        logger.info(f"✅ 找到有效MP3: {song_id} @ {d.date()}")
                        return url
                    else:
                        logger.debug(f"无效MP3: {url} (Type: {content_type}, Size: {content_length//1024}KB)")
        except (requests.ConnectionError, requests.Timeout, requests.RequestException) as e:
            logger.debug(f"MP3检查失败 {url}: {str(e)[:50]}")
    return None

def get_song_info(song_id):
    """获取单首歌曲的元信息"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    try:
        # 修复URL协议 (添加冒号)
        url = f"https://www.9ku.com/play/{song_id}.htm"
        logger.info(f"🔍 请求: {url}")
        
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        
        # 内容类型验证
        if 'text/html' not in res.headers.get('Content-Type', ''):
            logger.warning(f"⚠️ 无效内容类型: {res.headers.get('Content-Type')}")
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        
        # 标题提取 (优先使用ID选择器)
        title_element = soup.find("h1", id="songName") or soup.find("h1")
        title = title_element.text.strip() if title_element else f"未知歌曲_{song_id}"
        
        # 歌手提取
        artist_element = soup.find("h2", id="artistName") or soup.find("h2")
        artist = artist_element.text.strip() if artist_element else "未知歌手"

        info = {
            "song_id": song_id,
            "title": title,
            "artist": artist,
            "play_url": url,
            "mp3_url": None,
            "has_lyric": False,
            "album": None,
            "release_date": None
        }

        # 专辑信息提取
        song_info_div = soup.find("div", class_="songInfo") or soup.find("div", class_="songText")
        if song_info_div:
            for p in song_info_div.find_all("p"):
                text = p.get_text(strip=True)
                if "发行时间：" in text:
                    info["release_date"] = text.split("发行时间：")[1].split("&")[0].strip()
                if "所属专辑：" in text:
                    a_tag = p.find("a")
                    if a_tag:
                        info["album"] = a_tag.get_text(strip=True)

        # 歌词检查
        if soup.find("textarea", id="lrc_content"):
            info["has_lyric"] = True
            info["lyric_url"] = f"https://www.9ku.com/lyric/{song_id}.htm"

        # MP3查找
        mp3_url = find_mp3_url(song_id, INITIAL_DATE)
        info["mp3_url"] = mp3_url
        
        logger.info(f"✅ 成功解析: {title} - {artist} (ID:{song_id})")
        return info
        
    except requests.HTTPError as e:
        status = e.response.status_code
        logger.warning(f"🚫 HTTP错误 {song_id}: {status}")
        log_failed(song_id, f"HTTP_{status}")
        return None
    except requests.RequestException as e:
        logger.warning(f"🚫 请求异常 {song_id}: {str(e)[:50]}")
        log_failed(song_id, f"REQ_EXCEPTION")
        return None
    except Exception as e:
        logger.error(f"🚫 解析异常 {song_id}: {str(e)[:100]}", exc_info=True)
        log_failed(song_id, f"PARSE_ERROR")
        return None

def crawl_songs():
    """主爬取函数"""
    ensure_directories()
    songs = load_songs()
    existing_ids = {s["song_id"] for s in songs}
    
    total_ids = END_ID - START_ID + 1
    new_count = 0
    
    logger.info(f"📊 任务统计: 共{total_ids}首 | 已存在{len(existing_ids)}首 | 待爬取{total_ids - len(existing_ids)}首")
    
    # 创建任务列表 (跳过已存在)
    todo_ids = [sid for sid in range(START_ID, END_ID + 1) if sid not in existing_ids]
    random.shuffle(todo_ids)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(get_song_info, song_id): song_id for song_id in todo_ids}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            song_id = futures[future]
            try:
                info = future.result()
                if info:
                    songs.append(info)
                    new_count += 1
                    logger.info(f"🎵 进度: {i+1}/{len(todo_ids)} | 新增: {new_count}/{BATCH_SIZE}")
                    
                    # 批量保存
                    if new_count >= BATCH_SIZE:
                        if save_songs(songs):
                            new_count = 0
            except Exception as e:
                logger.error(f"🔥 处理异常 {song_id}: {str(e)[:100]}", exc_info=True)
            
            # 动态延迟 (0.3-1.5秒)
            time.sleep(random.uniform(0.3, 1.5))
    
    # 最终保存
    save_songs(songs)
    success_count = len([s for s in songs if s.get("mp3_url")])
    logger.info(f"🎉 爬取完成! 总计: {len(songs)}首 | 含MP3: {success_count}首 | 失败: {len(todo_ids) - len(songs)}首")

if __name__ == "__main__":
    try:
        crawl_songs()
    except KeyboardInterrupt:
        logger.warning("⛔ 用户中断，尝试保存数据...")
        # 立即保存当前进度
        import traceback
        traceback.print_exc()
    except Exception as e:
        logger.error(f"💥 程序崩溃: {str(e)}", exc_info=True)