<?php
$dsn = 'mysql:host=mysql.sqlpub.com;dbname=dakaca';
$user = 'dakaca007';
$password = 'Kgds63EecpSlAtYR';

try {
    $pdo = new PDO($dsn, $user, $password, [
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4"
    ]);
    // 设置PDO错误模式为异常
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // 查询user表的数据
    $sql = "SELECT * FROM user";
    $stmt = $pdo->query($sql);

    // 输出数据
    $users = $stmt->fetchAll(PDO::FETCH_ASSOC);
    if (count($users) > 0) {
        foreach ($users as $user) {
            echo "ID: " . $user["id"]. " - Username: " . $user["first_name"]. " - 
 Lastname: " . $user["last_name"]. " - Email: " . $user["email"]. "<br>";
        }
    } else {
        echo "user表中没有数据";
    }
} catch (PDOException $e) {
    echo "连接失败: " . $e->getMessage();
}
?>
