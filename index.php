<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>主页</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .navbar {
            overflow: hidden;
            background-color: #333;
        }
        .navbar a {
            float: left;
            display: block;
            color: white;
            text-align: center;
            padding: 14px 20px;
            text-decoration: none;
        }
        .navbar a:hover {
            background-color: #ddd;
            color: black;
        }
        .container {
            padding: 20px;
        }
        .form-container {
            margin-bottom: 20px;
        }
        .form-container form {
            margin-bottom: 10px;
        }
        .forum, .news, .messages {
            margin-bottom: 20px;
        }
        h2 {
            color: #333;
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
                用户名: <input type="text" name="username" required><br>
                密码: <input type="password" name="password" required><br>
                <button type="submit">注册</button>
            </form>
            
            <h2>登录</h2>
            <form action="login.php" method="post">
                用户名: <input type="text" name="username" required><br>
                密码: <input type="password" name="password" required><br>
                <button type="submit">登录</button>
            </form>
        </div>
        
        <div id="forum" class="forum">
            <h2>论坛发布栏</h2>
            <form action="post_forum.php" method="post">
                标题: <input type="text" name="title" required><br>
                内容: <textarea name="content" required></textarea><br>
                <button type="submit">发布</button>
            </form>
        </div>
        
        <div id="news" class="news">
            <h2>新闻栏</h2>
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
                    $sql = "SELECT * FROM news";
                    $stmt = $pdo->query($sql);
                    $news = $stmt->fetchAll(PDO::FETCH_ASSOC);

                    if (count($news) > 0) {
                        foreach ($news as $item) {
                            echo "<h3>" . $item["title"] . "</h3>";
                            echo "<p>" . $item["content"] . "</p>";
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
                姓名: <input type="text" name="name" required><br>
                留言: <textarea name="message" required></textarea><br>
                <button type="submit">提交</button>
            </form>
            <div>
                <?php
                // 查询留言表的数据
                $sql = "SELECT * FROM messages";
                $stmt = $pdo->query($sql);
                $messages = $stmt->fetchAll(PDO::FETCH_ASSOC);

                if (count($messages) > 0) {
                    foreach ($messages as $msg) {
                        echo "<p><strong>" . $msg["name"] . ":</strong> " . $msg["message"] . "</p>";
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
