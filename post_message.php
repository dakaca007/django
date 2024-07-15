<?php
$dsn = 'mysql:host=mysql.sqlpub.com;dbname=dakaca';
$user = 'dakaca007';
$password = 'Kgds63EecpSlAtYR';

try {
    $pdo = new PDO($dsn, $user, $password, [
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4"
    ]);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $name = $_POST['name'];
        $message = $_POST['message'];

        $sql = "INSERT INTO messages (name, message) VALUES (:name, :message)";
        $stmt = $pdo->prepare($sql);
        $stmt->bindParam(':name', $name, PDO::PARAM_STR);
        $stmt->bindParam(':message', $message, PDO::PARAM_STR);
        
        if ($stmt->execute()) {
            echo "留言插入成功！";
        } else {
            echo "插入留言时出错，请重试。";
        }
    }
} catch (PDOException $e) {
    die("数据库操作失败: " . $e->getMessage());
}
?>
