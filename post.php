<?php
session_start();
require_once 'database.php';

$userId = $_SESSION['UserID'];
$pdo = openDatabaseConnection();

$sql = "SELECT p.*, u.Username, c.CategoryName FROM Posts p JOIN Users u ON p.AuthorID = u.UserID JOIN Categories c ON p.CategoryID = c.CategoryID WHERE PostID = ?";
$stmt = $pdo->prepare($sql);
$stmt->execute([$userId]);
$post = $stmt->fetch(PDO::FETCH_ASSOC);

$sql = "SELECT c.*, u.Username FROM Comments c JOIN Users u ON c.AuthorID = u.UserID WHERE PostID = ? ORDER BY CommentDate ASC";
$stmt = $pdo->prepare($sql);
$stmt->execute([$userId]);
$comments = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<?php require_once 'templates/header.php'; ?>

<article>
    <h2><?php echo $post['Title']; ?></h2>
    <p><?php echo $post['Content']; ?></p>
    <p>作者: <?php echo $post['Username']; ?> | 分类: <?php echo $post['CategoryName']; ?> | 日期: <?php echo $post['PostDate']; ?></p>
    <?php if (isset($_SESSION['UserID']) && $_SESSION['UserID'] == $post['AuthorID']): ?>
        <a href="edit_post.php?id=<?php echo $post['PostID']; ?>">编辑</a> | <a href="delete_post.php?id=<?php echo $post['PostID']; ?>">删除</a>
    <?php endif; ?>
</article>

<h3>评论</h3>
<?php foreach ($comments as $comment): ?>
    <div>
        <p><?php echo $comment['Content']; ?></p>
        <p>评论者: <?php echo $comment['Username']; ?> | 日期: <?php echo $comment['CommentDate']; ?></p>
    </div>
<?php endforeach; ?>

<?php if (isset($_SESSION['UserID'])): ?>
    <h3>添加评论</h3>
    <form method="post" action="comment.php?id=<?php echo $postID; ?>">
        内容: <textarea name="content" required></textarea><br>
        <button type="submit">评论</button>
    </form>
<?php endif; ?>

<?php require_once 'templates/footer.php'; ?>
