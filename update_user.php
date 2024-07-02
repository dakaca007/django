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
$first_name = $_GET['first_name'];
$last_name = $_GET['last_name'];
$email = $_GET['email'];

$sql = "UPDATE user SET first_name='$first_name', last_name='$last_name', email='$email' WHERE id=$id";
if ($conn->query($sql) === TRUE) {
    echo "记录更新成功";
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
