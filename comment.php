<?php
session_start();
require_once 'includes/database.php';

if (!isset($_SESSION['UserID'])) {
    header("Location: login.php");
    exit();
}

$postID = $_GET['id'];

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $pdo = openDatabaseConnection();
    $content = $_POST['content'];
    $authorID = $_SESSION['UserID'];

    $sql = "INSERT INTO Comments (PostID, AuthorID, Content) VALUES (?, ?, ?)";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$postID, $authorID, $content]);

    header("Location: post.php?id=$postID");
    exit();
}
?>

<?php require_once 'templates/header.php'; ?>

<h2>添加评论</h2>
<form method="post">
    内容: <textarea name="content" required></textarea><br>
    <button type="submit">评论</button>
</form>

<?php require_once 'templates/footer.php'; ?>
