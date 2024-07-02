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

$first_name = $_GET['first_name'];
$last_name = $_GET['last_name'];
$email = $_GET['email'];

$sql = "INSERT INTO user (first_name, last_name, email) VALUES ('$first_name', '$last_name', '$email')";
if ($conn->query($sql) === TRUE) {
    echo "新记录插入成功";
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
