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
                <li><a href="login.php">登录</a></li>
                <li><a href="register.php">注册</a></li>
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
                <?php
                require_once 'database.php';
                $pdo = openDatabaseConnection();
                
                $sql = "SELECT CategoryName FROM Categories";
                $stmt = $pdo->query($sql);
                
                while($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                    echo "<li><a href='#'>" . $row['CategoryName'] . "</a></li>";
                }
                ?>
            </ul>
        </section>

        <section class="posts">
            <h2>最新帖子</h2>
            <?php
            require_once 'database.php';
            $pdo = openDatabaseConnection();
            
            $sql = "SELECT Title, Content, Username, PostDate FROM Posts JOIN Users ON Posts.AuthorID = Users.UserID ORDER BY PostDate DESC LIMIT 5";
            $stmt = $pdo->query($sql);
            
            while($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                echo "<article class='post'>";
                echo "<h3><a href='#'>" . $row['Title'] . "</a></h3>";
                echo "<p>作者：" . $row['Username'] . " | 发布时间：" . $row['PostDate'] . "</p>";
                echo "<p>" . $row['Content'] . "</p>";
                echo "</article>";
            }
            ?>
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
