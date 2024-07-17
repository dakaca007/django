<?php
session_start();
require_once 'database.php';

if (!isset($_SESSION['UserID'])) {
    header("Location: login.php");
    exit();
}

$postID = $_GET['id'];
$pdo = openDatabaseConnection();

$sql = "DELETE FROM Posts WHERE PostID = ? AND AuthorID = ?";
$stmt = $pdo->prepare($sql);
$stmt->execute([$postID, $_SESSION['UserID']]);

header("Location: index.php");
exit();
?>
