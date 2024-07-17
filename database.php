<?php
function openDatabaseConnection() {
    $dbHost = 'mysql.sqlpub.com';
    $dbName = 'dakacan';
    $dbUsername = 'dakacan007';
    $dbPassword = '4EQ9JZDnPSg36FXy';

    $pdo = new PDO("mysql:host=$dbHost;dbname=$dbName", $dbUsername, $dbPassword);
    
    // 设置PDO属性
    $pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    return $pdo;
}
?>
