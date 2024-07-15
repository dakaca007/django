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

    // Check if the request method is POST
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        // Get the form data
        $title = $_POST['title'];
        $content = $_POST['content'];

        // Validate the data (add your validation logic here)
        if (empty($title) || empty($content)) {
            // Handle validation errors (e.g., display an error message)
            echo "标题和内容不能为空！";
        } else {
            // Prepare the SQL query
            $sql = "INSERT INTO news (title, content) VALUES (:title, :content)";
            $stmt = $pdo->prepare($sql);

            // Bind the values
            $stmt->bindParam(':title', $title, PDO::PARAM_STR);
            $stmt->bindParam(':content', $content, PDO::PARAM_STR);

            // Execute the query
            if ($stmt->execute()) {
                echo "新闻插入成功！";
            } else {
                echo "插入新闻时出错，请重试。";
            }
        }
    }
} catch (PDOException $e) {
    die("数据库操作失败: " . $e->getMessage());
}
?>
