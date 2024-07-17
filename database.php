<?php
function openDatabaseConnection() {
    $dbHost = 'mysql.sqlpub.com';
    $dbName = 'dakacan';
    $dbUsername = 'dakacan007';
    $dbPassword = '4EQ9JZDnPSg36FXy';

    return new PDO("mysql:host=$dbHost;dbname=$dbName", $dbUsername, $dbPassword);
}
?>
