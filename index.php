<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>主页</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 0;
        }
        .navbar {
            overflow: hidden;
            background-color: #007BFF;
            padding: 10px 0;
        }
        .navbar a {
            float: left;
            display: block;
            color: white;
            text-align: center;
            padding: 14px 20px;
            text-decoration: none;
            font-weight: bold;
        }
        .navbar a:hover {
            background-color: #0056b3;
        }
        .container {
            padding: 20px;
            max-width: 1200px;
            margin: auto;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        .form-container, .forum, .news, .messages {
            margin-bottom: 20px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #fff;
        }
        h2 {
            color: #333;
            border-bottom: 2px solid #007BFF;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        form {
            display: flex;
            flex-direction: column;
        }
        form input, form textarea {
            margin-bottom: 10px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        form button {
            padding: 10px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        form button:hover {
            background-color: #0056b3;
        }
        .forum-post, .news-item, .message-item {
            margin-bottom: 20px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        .forum-post h3, .news-item h3 {
            margin-top: 0;
        }
        .message-item strong {
            display: block;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="#home">主页</a>
        <a href="#forum">论坛</a>
        <a href="#news">新闻</a>
        <a href="#messages">留言</a>
    </div>
    
    <div class="container">
        <div class="form-container">
            <h2>注册</h2>
            <form action="register.php" method="post">
                用户名: <input type="text" name="username" required>
                密码: <input type="password" name="password" required>
                <button type="submit">注册</button>
            </form>
            
            <h2>登录</h2>
            <form action="login.php" method="post">
                用户名: <input type="text" name="username" required>
                密码: <input type="password" name="password" required>
                <button type="submit">登录</button>
            </form>
        </div>
        
        <div id="forum" class="forum">
            <h2>论坛发布栏</h2>
            <form action="post_forum.php" method="post">
                标题: <input type="text" name="title" required>
                内容: <textarea name="content" required></textarea>
                <button type="submit">发布</button>
            </form>
            <div>
                <?php
                // Connect to the database
                $dsn = 'mysql:host=mysql.sqlpub.com;dbname=dakaca';
                $user = 'dakaca007';
                $password = 'Kgds63EecpSlAtYR';

                try {
                    $pdo = new PDO($dsn, $user, $password, [
                        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4"
                    ]);
                    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

                    // Query for forum posts
                    $sql = "SELECT * FROM forum ORDER BY id DESC"; // Assuming 'id' is the primary key in your forum table
                    $stmt = $pdo->query($sql);
                    $forumPosts = $stmt->fetchAll(PDO::FETCH_ASSOC);

                    if (count($forumPosts) > 0) {
                        foreach ($forumPosts as $post) {
                            echo "<div class='forum-post'>";
                            echo "<h3>" . htmlspecialchars($post["title"]) . "</h3>";
                            echo "<p>" . nl2br(htmlspecialchars($post["content"])) . "</p>";
                            echo "</div>";
                        }
                    } else {
                        echo "论坛中没有数据";
                    }
                } catch (PDOException $e) {
                    echo "连接失败: " . $e->getMessage();
                }
                ?>
            </div>
        </div>
        
        <div id="news" class="news">
            <h2>新闻栏</h2>
            <form action="post_news.php" method="post">
                标题: <input type="text" name="title" required>
                内容: <textarea name="content" required></textarea>
                <button type="submit">提交</button>
            </form>
            <div>
                <?php
                // 连接数据库
                $dsn = 'mysql:host=mysql.sqlpub.com;dbname=dakaca';
                $user = 'dakaca007';
                $password = 'Kgds63EecpSlAtYR';

                try {
                    $pdo = new PDO($dsn, $user, $password, [
                        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4"
                    ]);
                    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

                    // 查询新闻表的数据
                    $sql = "SELECT * FROM news ORDER BY id DESC";
                    $stmt = $pdo->query($sql);
                    $news = $stmt->fetchAll(PDO::FETCH_ASSOC);

                    if (count($news) > 0) {
                        foreach ($news as $item) {
                            echo "<div class='news-item'>";
                            echo "<h3>" . htmlspecialchars($item["title"]) . "</h3>";
                            echo "<p>" . nl2br(htmlspecialchars($item["content"])) . "</p>";
                            echo "</div>";
                        }
                    } else {
                        echo "新闻表中没有数据";
                    }
                } catch (PDOException $e) {
                    echo "连接失败: " . $e->getMessage();
                }
                ?>
            </div>
        </div>
        
        <div id="messages" class="messages">
            <h2>留言栏</h2>
            <form action="post_message.php" method="post">
                姓名: <input type="text" name="name" required>
                留言: <textarea name="message" required></textarea>
                <button type="submit">提交</button>
            </form>
            <div>
                <?php
                // 查询留言表的数据
                $sql = "SELECT * FROM messages ORDER BY id DESC";
                $stmt = $pdo->query($sql);
                $messages = $stmt->fetchAll(PDO::FETCH_ASSOC);

                if (count($messages) > 0) {
                    foreach ($messages as $msg) {
                        echo "<div class='message-item'>";
                        echo "<strong>" . htmlspecialchars($msg["name"]) . ":</strong> ";
                        echo "<p>" . nl2br(htmlspecialchars($msg["message"])) . "</p>";
                        echo "</div>";
                    }
                } else {
                    echo "留言表中没有数据";
                }
                ?>
            </div>
        </div>
    </div>
</body>
</html>
