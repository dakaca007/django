<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>自动切换 & 下载视频播放器</title>
  <style>
    body { display: flex; flex-direction: column; align-items: center; padding: 20px; font-family: sans-serif; }
    #player { max-width: 100%; border: 1px solid #ccc; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }
    #controls { margin-top: 10px; }
    #loading { margin-top: 10px; color: #666; }
    #history { margin-top: 20px; width: 100%; max-width: 600px; }
    #history h2 { margin-bottom: 8px; }
    #history ul { list-style: none; padding: 0; }
    #history li { display: flex; justify-content: space-between; align-items: center; padding: 6px 8px; border-bottom: 1px solid #eee; }
    #history li button { margin-left: 8px; }
  </style>
</head>
<body>
  <h1>自动切换 & 下载视频播放器</h1>
  <video id="player" controls autoplay></video>
  <div id="controls">
    <button id="nextBtn">下一个视频</button>
  </div>
  <div id="loading">正在加载视频…</div>

  <div id="history">
    <h2>播放历史</h2>
    <ul id="historyList"></ul>
  </div>

  <script>
    const apiEndpoint = 'https://api.kuleu.com/api/MP4_xiaojiejie?type=json';
    const player = document.getElementById('player');
    const loadingEl = document.getElementById('loading');
    const nextBtn = document.getElementById('nextBtn');
    const historyList = document.getElementById('historyList');
    const HISTORY_KEY = 'videoHistory';
    const MAX_HISTORY = 5000;

    // 读取历史记录
    function loadHistory() {
      const json = localStorage.getItem(HISTORY_KEY) || '[]';
      try {
        return JSON.parse(json);
      } catch {
        return [];
      }
    }

    // 保存历史记录
    function saveHistory(list) {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(list));
    }

    // 更新历史列表 UI
    function renderHistory() {
      const list = loadHistory();
      historyList.innerHTML = '';
      list.forEach((item) => {
        const li = document.createElement('li');
        const time = new Date(item.time).toLocaleString();
        li.textContent = `${time}`;

        const buttons = document.createElement('div');
        const playBtn = document.createElement('button');
        playBtn.textContent = '播放';
        playBtn.addEventListener('click', () => playFromHistory(item.url));

        const dlBtn = document.createElement('button');
        dlBtn.textContent = '下载';
        dlBtn.addEventListener('click', () => downloadVideo(item.url));

        buttons.append(playBtn, dlBtn);
        li.appendChild(buttons);
        historyList.appendChild(li);
      });
    }

    // 播放历史视频
    async function playFromHistory(url) {
      player.src = url;
      await player.load();
      await player.play();
      loadingEl.textContent = '';
    }

   // 下载视频
    async function downloadVideo(url) {
      try {
        const resp = await fetch(url);
        const blob = await resp.blob();
        const a = document.createElement('a');
        const fileName = `video_${Date.now()}.mp4`;
        a.href = URL.createObjectURL(blob);
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(a.href);
      } catch (err) {
        console.error('下载失败', err);
        alert('下载失败，请稍后重试');
      }
    }


async function loadNextVideo() {
  loadingEl.textContent = '正在加载视频...';

  try {
    const resp = await fetch(apiEndpoint);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    if (data.code !== 200 || !data.mp4_video) {
      throw new Error(data.msg || '返回数据不包含视频链接');
    }

    const url = data.mp4_video;

    // 更新播放器
    player.src = url;
    await player.load();
    await player.play();
    loadingEl.textContent = '';

    // 保存历史
    const history = loadHistory();
    history.unshift({ url, time: Date.now() });
    if (history.length > MAX_HISTORY) history.pop();
    saveHistory(history);
    renderHistory();

    // 自动下载
    downloadVideo(url);
  } catch (err) {
    console.error('加载视频失败', err);
    loadingEl.textContent = '视频加载失败,正在尝试下一个视频...';

    // 尝试加载下一个视频,但最多尝试 3 次
    let retryCount = 0;
    const maxRetries = 3;
    const retryDelay = 5000; // 1 秒

    const retryLoadNextVideo = async () => {
      if (retryCount < maxRetries) {
        retryCount++;
        try {
          await loadNextVideo();
        } catch (retryErr) {
          console.error('重试加载视频失败', retryErr);
          loadingEl.textContent = '视频加载失败,正在尝试下一个视频...';
          setTimeout(retryLoadNextVideo, retryDelay);
        }
      } else {
        loadingEl.textContent = '无法加载任何视频,请稍后重试';
      }
    };

    setTimeout(retryLoadNextVideo, retryDelay);
  }
}
// 事件绑定
player.addEventListener('ended', loadNextVideo);
nextBtn.addEventListener('click', loadNextVideo);
window.addEventListener('DOMContentLoaded', () => {
  renderHistory();
  loadNextVideo();
});

    // 事件绑定
    player.addEventListener('ended', loadNextVideo);
    nextBtn.addEventListener('click', loadNextVideo);
    window.addEventListener('DOMContentLoaded', () => {
      renderHistory();
      loadNextVideo();
    });
  </script>
</body>
</html>
