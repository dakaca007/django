<?php
function openDatabaseConnection() {
    $dbHost = 'mysql.sqlpub.com';
    $dbName = 'dakacan';
    $dbUsername = 'dakacan007';
    $dbPassword = '4EQ9JZDnPSg36FXy';

    return new PDO("mysql:host=$dbHost;dbname=$dbName", $dbUsername, $dbPassword);
}

function getCategories() {
    $pdo = openDatabaseConnection();
    $sql = "SELECT CategoryName FROM Categories";
    $stmt = $pdo->query($sql);

    while($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        echo "<li><a href='#'>" . $row['CategoryName'] . "</a></li>";
    }
}

function getLatestPosts() {
    $pdo = openDatabaseConnection();
    $sql = "SELECT Title, Content, Username, PostDate FROM Posts JOIN Users ON Posts.AuthorID = Users.UserID ORDER BY PostDate DESC LIMIT 5";
    $stmt = $pdo->query($sql);

    while($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        echo "<article class='post'>";
        echo "<h3><a href='#'>" . $row['Title'] . "</a></h3>";
        echo "<p>作者：" . $row['Username'] . " | 发布时间：" . $row['PostDate'] . "</p>";
        echo "<p>" . $row['Content'] . "</p>";
        echo "</article>";
    }
}
?>
