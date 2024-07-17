<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>在问论坛</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <div class="logo">
            <h1>在问论坛</h1>
        </div>
        <nav>
            <ul>
                <li><a href="#">首页</a></li>
                <li><a href="#">热门话题</a></li>
                <li><a href="#">最新发布</a></li>
                <li><a href="#">分类</a></li>
                <li><a href="#">关于我们</a></li>
                <li><a href="#">登录</a></li>
                <li><a href="#">注册</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section class="search-bar">
            <input type="text" id="searchInput" placeholder="搜索帖子...">
            <button type="submit" onclick="searchPosts()">搜索</button>
        </section>

        <section class="categories">
            <h2>论坛分类</h2>
            <ul>
                <?php include 'forum_backend.php'; getCategoies(); ?>
            </ul>
        </section>

        <section class="posts">
            <h2>最新帖子</h2>
            <?php include 'forum_backend.php'; getLatestPosts(); ?>
        </section>
    </main>

    <footer>
        <p>&copy; 2024 在问论坛. 保留所有权利.</p>
    </footer>

    <script>
        function searchPosts() {
            // 使用JavaScript与后端交互，根据搜索条件触发后端程序进行搜索
        }
    </script>
</body>
</html>
