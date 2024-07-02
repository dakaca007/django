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

$sql = "SELECT * FROM user";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    $users = [];
    while($row = $result->fetch_assoc()) {
        $users[] = $row;
    }
    echo json_encode($users);
} else {
    echo "0 结果";
}

$conn->close();
?>
