<?php
header('Content-Type: text/html; charset=utf-8');

$servername = "mysql.sqlpub.com";
$username = "dakaca007";
$password = "Kgds63EecpSlAtYR";
$dbname = "dakaca";
$port = 3306;

$conn = new mysqli($servername, $username, $password, $dbname, $port);

if ($conn->connect_error) {
    die("连接失败: " . $conn->connect_error);
}

$conn->set_charset("utf8");

$id = $_GET['id'];

$sql = "SELECT * FROM user WHERE id=$id";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    $user = $result->fetch_assoc();
    echo json_encode($user);
} else {
    echo "0 结果";
}

$conn->close();
?>
