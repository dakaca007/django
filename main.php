<?php
session_start();
require_once 'database.php';

$pdo = openDatabaseConnection();
$categories = $pdo->query("SELECT * FROM Categories")->fetchAll(PDO::FETCH_ASSOC);
$posts = $pdo->query("SELECT p.*, u.Username, c.CategoryName FROM Posts p JOIN Users u ON p.AuthorID = u.UserID JOIN Categories c ON p.CategoryID = c.CategoryID ORDER BY PostDate DESC")->fetchAll(PDO::FETCH_ASSOC);
?>

<?php require_once 'templates/header.php'; ?>

<h2>帖子列表</h2>
<?php foreach ($categories as $category): ?>
    <h3><?php echo $category['CategoryName']; ?></h3>
    <?php foreach ($posts as $post): ?>
        <?php if ($post['CategoryID'] == $category['CategoryID']): ?>
            <article>
                <h4><a href="post.php?id=<?php echo $post['PostID']; ?>"><?php echo $post['Title']; ?></a></h4>
                <p><?php echo $post['Content']; ?></p>
                <p>作者: <?php echo $post['Username']; ?> | 日期: <?php echo $post['PostDate']; ?></p>
                <?php if (isset($_SESSION['UserID']) && $_SESSION['UserID'] == $post['AuthorID']): ?>
                    <a href="edit_post.php?id=<?php echo $post['PostID']; ?>">编辑</a> | <a href="delete_post.php?id=<?php echo $post['PostID']; ?>">删除</a>
                <?php endif; ?>
            </article>
        <?php endif; ?>
    <?php endforeach; ?>
<?php endforeach; ?>

<?php require_once 'templates/footer.php'; ?>
