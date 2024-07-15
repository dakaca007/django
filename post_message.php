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
