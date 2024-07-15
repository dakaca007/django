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
        $username = $_POST['username'];
        $password = password_hash($_POST['password'], PASSWORD_BCRYPT);

        $sql = "INSERT INTO users (username, password) VALUES (:username, :password)";
        $stmt = $pdo->prepare($sql);
        $stmt->bindParam(':username', $username);
        $stmt->bindParam(':password', $password);
        $stmt->execute();

        echo "注册成功！";
    }
} catch (PDOException $e) {
    echo "连接失败: " . $e->getMessage();
}
?>
