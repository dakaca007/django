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
import logging
from urllib.parse import urlparse
import psutil
import signal
import sys
from typing import Optional, Dict, Tuple, List

# 配置项
START_ID = 860000
END_ID = 960000
INITIAL_DATE = datetime(2017, 3, 16)
MAX_DATE_SHIFT = 7
PROGRESS_JSON = "progress.json"
FAILED_FILE = "failed.json"  # 改为JSON格式记录更多信息
SONGS_META_FILE = "songs_meta.json"
BATCH_SIZE = 20
MAX_WORKERS = 5  # 根据CPU核心数动态调整
MAX_RETRIES = 3
REQUEST_TIMEOUT = 10
REQUEST_DELAY = (0.5, 1.5)  # 请求延迟范围
MEMORY_LIMIT_MB = 512  # 内存限制

# 代理配置 (可选)
PROXY = None  # 例如: {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GracefulExiter:
    """优雅退出处理"""
    def __init__(self):
        self.shutdown = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logger.info("接收到终止信号，准备优雅退出...")
        self.shutdown = True

class MemoryMonitor(threading.Thread):
    """内存监控线程"""
    def __init__(self, limit_mb):
        super().__init__(daemon=True)
        self.limit = limit_mb * 1024 * 1024  # 转换为字节
        self.alert_threshold = 0.9 * self.limit
        self.running = True
        
    def run(self):
        while self.running:
            mem = psutil.Process().memory_info().rss
            if mem > self.alert_threshold:
                logger.warning(f"内存使用接近限制: {mem / (1024*1024):.2f}MB")
            if mem > self.limit:
                logger.error(f"内存超出限制({self.limit/(1024*1024):.2f}MB)，准备清理缓存")
                extract_song_info.cache_clear()
            time.sleep(5)
    
    def stop(self):
        self.running = False

class SafeSession(requests.Session):
    """带重试和限流的Session"""
    def __init__(self):
        super().__init__()
        self.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        self.last_request_time = 0
        self.proxies = PROXY
        
    def request(self, method, url, **kwargs):
        # 请求限流
        elapsed = time.time() - self.last_request_time
        delay = random.uniform(*REQUEST_DELAY)
        if elapsed < delay:
            time.sleep(delay - elapsed)
        
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        self.last_request_time = time.time()
        
        for attempt in range(MAX_RETRIES):
            try:
                response = super().request(method, url, **kwargs)
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 10))
                    logger.warning(f"请求过于频繁，等待 {retry_after} 秒后重试")
                    time.sleep(retry_after)
                    continue
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                wait_time = (2 ** attempt) + random.random()
                logger.warning(f"请求失败: {e}, 尝试 {attempt + 1}/{MAX_RETRIES}, 等待 {wait_time:.1f}s")
                time.sleep(wait_time)

session = SafeSession()

def load_progress() -> Tuple[int, datetime]:
    """加载进度"""
    try:
        if os.path.exists(PROGRESS_JSON):
            with open(PROGRESS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            sid = int(data.get("song_id", START_ID))
            ldate = datetime.fromisoformat(data.get("last_date", INITIAL_DATE.isoformat()))
            logger.info(f"从进度文件恢复: ID={sid}, 日期={ldate.date()}")
            return sid, ldate
    except Exception as e:
        logger.error(f"加载进度文件失败: {e}")
    return START_ID, INITIAL_DATE

def save_progress(song_id: int, last_date: datetime):
    """保存进度"""
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tmp:
            json.dump({
                "song_id": song_id,
                "last_date": last_date.date().isoformat(),
                "updated_at": datetime.now().isoformat()
            }, tmp)
        shutil.move(tmp.name, PROGRESS_JSON)
    except Exception as e:
        logger.error(f"保存进度失败: {e}")

def log_failure(song_id: int, error: str, context: Optional[Dict] = None):
    """记录失败信息"""
    try:
        failures = []
        if os.path.exists(FAILED_FILE):
            try:
                with open(FAILED_FILE, "r", encoding="utf-8") as f:
                    failures = json.load(f)
            except json.JSONDecodeError:
                pass
        
        failures.append({
            "song_id": song_id,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        })
        
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tmp:
            json.dump(failures, tmp, ensure_ascii=False, indent=2)
        shutil.move(tmp.name, FAILED_FILE)
    except Exception as e:
        logger.error(f"记录失败信息失败: {e}")

def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    # 保留中文、英文、数字和常用符号
    keep_chars = (" ", "_", "-", "(", ")", "[", "]", "{", "}", "+", "=")
    return "".join(c for c in name if c.isalnum() or c in keep_chars).strip()

@lru_cache(maxsize=2048)
def extract_song_info(song_id: int) -> Optional[Dict]:
    """提取歌曲信息(带缓存)"""
    def _extract():
        try:
            url = f"https://www.9ku.com/play/{song_id}.htm"
            logger.debug(f"获取歌曲信息: {url}")
            res = session.get(url)
            
            if res.status_code == 404:
                logger.info(f"歌曲不存在(ID:{song_id})")
                return None
                
            strainer = SoupStrainer(["h1", "h2", "div", "textarea"])
            soup = BeautifulSoup(res.text, "html.parser", parse_only=strainer)
            
            title_elem = soup.find("h1")
            artist_elem = soup.find("h2")
            
            if not title_elem or not artist_elem:
                logger.warning(f"页面结构异常(ID:{song_id})")
                return None
                
            title = title_elem.text.strip() or f"unknown_{song_id}"
            artist = artist_elem.text.strip() or "unknown_artist"
            
            # 提取发行信息和专辑
            release = album = None
            div = soup.find("div", class_="songText")
            if div:
                for p in div.find_all("p", class_="p1"):
                    text = p.get_text()
                    if "发行时间：" in text: 
                        release = text.split("发行时间：")[1].split("&")[0].strip()
                    if "所属专辑：" in text: 
                        album = p.find("a").text.strip() if p.find("a") else None
            
            # 检查歌词
            lyric = soup.find("textarea", id="lrc_content")
            
            return {
                "song_id": song_id,
                "title": title,
                "artist": artist,
                "release_date": release,
                "album": album,
                "has_lyric": bool(lyric),
                "lyric_url": f"https://www.9ku.com/lyric/{song_id}.htm",
                "page_url": url,
                "fetched_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"提取歌曲信息失败(ID:{song_id}): {e}")
            raise
    
    return retry_operation(_extract, song_id)

def retry_operation(operation, *args, **kwargs):
    """带重试的操作封装"""
    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            return operation(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            last_exception = e
            logger.warning(f"操作失败(尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
        except Exception as e:
            last_exception = e
            logger.warning(f"操作失败(尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
        
        if attempt < MAX_RETRIES - 1:
            wait = (2 ** attempt) + random.random()
            logger.info(f"等待 {wait:.1f}秒后重试...")
            time.sleep(wait)
    
    logger.error(f"操作最终失败: {last_exception}")
    return None

def url_exists(url: str) -> Optional[str]:
    """检查URL是否存在"""
    try:
        # 使用HEAD方法检查，节省带宽
        r = session.head(url, allow_redirects=True)
        if r.status_code == 200:
            # 检查内容类型是否为MP3
            content_type = r.headers.get('Content-Type', '')
            if 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
                return url
        return None
    except requests.exceptions.RequestException as e:
        logger.debug(f"URL检查失败: {url} - {e}")
        return None

def find_mp3_url(song_id: int, base_date: datetime) -> Tuple[Optional[str], datetime]:
    """查找MP3文件URL"""
    base_urls = [
        "https://music.jsbaidu.com/upload/128",
        "https://mp3.9ku.com/m4a/{song_id}.m4a",  # 备用URL模式
    ]
    
    dates = [base_date + timedelta(days=i) for i in range(MAX_DATE_SHIFT)]
    found_url = None
    found_date = base_date
    
    for base_url in base_urls:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 准备所有可能的URL
            futures = {}
            if "{song_id}" in base_url:
                url = base_url.format(song_id=song_id)
                futures[executor.submit(url_exists, url)] = ("static", base_date)
            else:
                for d in dates:
                    url = f"{base_url}/{d:%Y/%m/%d}/{song_id}.mp3"
                    futures[executor.submit(url_exists, url)] = ("date", d)
            
            # 检查结果
            for future in concurrent.futures.as_completed(futures):
                url_type, date = futures[future]
                url = future.result()
                if url:
                    found_url = url
                    found_date = date
                    logger.info(f"找到MP3(ID:{song_id} 类型:{url_type} 日期:{date.date()})")
                    # 取消其他未完成的任务
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    break
        
        if found_url:
            break
    
    if not found_url:
        logger.warning(f"未找到MP3(ID:{song_id})")
    
    return found_url, found_date

def safe_write_json(filename: str, data):
    """安全写入JSON文件"""
    tmpfd, tmpname = tempfile.mkstemp(suffix=".tmp", prefix="tmp_", dir=os.path.dirname(filename))
    try:
        with os.fdopen(tmpfd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        shutil.move(tmpname, filename)
    except Exception as e:
        logger.error(f"写入文件失败: {filename} - {e}")
        if os.path.exists(tmpname):
            os.remove(tmpname)
        raise

def meta_writer_thread(stop_event: threading.Event, meta_queue: queue.Queue):
    """元数据写入线程"""
    all_meta = []
    if os.path.exists(SONGS_META_FILE):
        try:
            with open(SONGS_META_FILE, "r", encoding="utf-8") as f:
                all_meta = json.load(f)
            logger.info(f"已加载 {len(all_meta)} 条现有元数据")
        except Exception as e:
            logger.error(f"读取元数据文件失败: {e}")

    batch = []
    last_write_time = time.time()
    batch_size = 0
    
    while not stop_event.is_set() or not meta_queue.empty():
        try:
            # 从队列获取元数据
            meta = meta_queue.get(timeout=1)
            batch.append(meta)
            batch_size += 1
            meta_queue.task_done()
            
            # 定期写入或批量达到一定大小
            current_time = time.time()
            if batch_size >= 10 or (current_time - last_write_time) > 30:
                try:
                    all_meta.extend(batch)
                    safe_write_json(SONGS_META_FILE, all_meta)
                    logger.info(f"已写入 {len(batch)} 条元数据到文件 (总计:{len(all_meta)})")
                    batch.clear()
                    batch_size = 0
                    last_write_time = current_time
                except Exception as e:
                    logger.error(f"写入元数据失败: {e}")
                    # 将失败的批次重新放回队列
                    for m in batch:
                        meta_queue.put(m)
                    batch.clear()
                    batch_size = 0
            
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"元数据写入线程异常: {e}")
    
    # 写入剩余批次
    if batch:
        try:
            all_meta.extend(batch)
            safe_write_json(SONGS_META_FILE, all_meta)
            logger.info(f"最终写入 {len(batch)} 条元数据 (总计:{len(all_meta)})")
        except Exception as e:
            logger.error(f"最终写入元数据失败: {e}")

def process_one(song_id: int, cur_date: datetime) -> Tuple[int, Optional[datetime]]:
    """处理单个歌曲"""
    logger.info(f"开始处理 ID: {song_id}")
    
    try:
        # 获取歌曲信息
        info = extract_song_info(song_id)
        if not info:
            log_failure(song_id, "无法提取歌曲信息")
            return song_id, None
        
        # 查找MP3 URL
        mp3_url, new_date = find_mp3_url(song_id, cur_date)
        if not mp3_url:
            log_failure(song_id, "未找到MP3文件", {"info": info})
            return song_id, None
        
        # 准备元数据
        filename = sanitize_filename(f"{info['title']}_{info['artist']}_{song_id}.mp3")
        
        meta_entry = {
            "song_id": song_id,
            "title": info["title"],
            "artist": info["artist"],
            "release_date": info.get("release_date"),
            "album": info.get("album"),
            "has_lyric": info["has_lyric"],
            "lyric_url": info["lyric_url"],
            "mp3_url": mp3_url,
            "filename": filename,
            "added_at": datetime.now().isoformat(),
            "source": "9ku",
            "info": info  # 包含原始信息
        }
        
        return song_id, (new_date, meta_entry)
        
    except Exception as e:
        logger.error(f"处理歌曲失败(ID:{song_id}): {e}")
        log_failure(song_id, str(e), {"traceback": str(sys.exc_info())})
        return song_id, None

def process_batch(batch_ids: List[int], cur_date: datetime, meta_queue: queue.Queue) -> datetime:
    """处理一批歌曲"""
    logger.info(f"开始处理批次: {batch_ids[0]}-{batch_ids[-1]}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_one, sid, cur_date): sid for sid in batch_ids}
        
        for future in concurrent.futures.as_completed(futures):
            sid, result = future.result()
            if result:
                new_date, meta = result
                cur_date = new_date
                meta_queue.put(meta)
                logger.info(f"成功处理 ID: {sid} (日期:{new_date.date()})")
            else:
                logger.warning(f"处理失败 ID: {sid}")
    
    return cur_date

def main():
    """主函数"""
    logger.info("启动9ku音乐爬虫")
    
    # 初始化监控和优雅退出
    exiter = GracefulExiter()
    memory_monitor = MemoryMonitor(MEMORY_LIMIT_MB)
    memory_monitor.start()
    
    # 加载进度
    current_id, current_date = load_progress()
    logger.info(f"当前进度: ID={current_id}, 日期={current_date.date()}")
    
    # 创建元数据队列和写入线程
    meta_queue = queue.Queue()
    stop_event = threading.Event()
    writer_thread = threading.Thread(
        target=meta_writer_thread,
        args=(stop_event, meta_queue),
        daemon=True
    )
    writer_thread.start()
    
    try:
        while current_id < END_ID and not exiter.shutdown:
            # 确定当前批次
            batch_end = min(current_id + BATCH_SIZE, END_ID)
            batch_ids = list(range(current_id, batch_end))
            
            # 处理批次
            current_date = process_batch(batch_ids, current_date, meta_queue)
            
            # 更新进度
            current_id = batch_end
            save_progress(current_id, current_date)
            logger.info(f"进度更新: ID={current_id}, 日期={current_date.date()}")
            
            # 检查内存使用
            mem = psutil.Process().memory_info().rss / (1024 * 1024)
            logger.info(f"内存使用: {mem:.2f}MB")
            
            # 随机延迟
            delay = random.uniform(*REQUEST_DELAY)
            logger.info(f"等待 {delay:.1f}秒后继续...")
            time.sleep(delay)
    
    except Exception as e:
        logger.error(f"主程序异常: {e}", exc_info=True)
    finally:
        # 清理工作
        logger.info("准备退出，等待队列处理完成...")
        stop_event.set()
        meta_queue.join()
        writer_thread.join()
        memory_monitor.stop()
        
        # 确保进度已保存
        save_progress(current_id, current_date)
        logger.info(f"最终进度: ID={current_id}, 日期={current_date.date()}")
        
        # 清理缓存
        extract_song_info.cache_clear()
        session.close()
        logger.info("爬虫已正常退出")

if __name__ == "__main__":
    main()
