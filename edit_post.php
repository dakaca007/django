<?php
session_start();
require_once 'database.php';

if (!isset($_SESSION['UserID'])) {
    header("Location: login.php");
    exit();
}

$postID = $_GET['id'];

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $pdo = openDatabaseConnection();
    $title = $_POST['title'];
    $content = $_POST['content'];
    $categoryID = $_POST['category'];
    $authorID = $_SESSION['UserID'];

    $sql = "UPDATE Posts SET Title = ?, Content = ?, CategoryID = ? WHERE PostID = ? AND AuthorID = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$title, $content, $categoryID, $postID, $authorID]);

    header("Location: index.php");
    exit();
} else {
    $pdo = openDatabaseConnection();
    $sql = "SELECT * FROM Posts WHERE PostID = ? AND AuthorID = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$postID, $_SESSION['UserID']]);
    $post = $stmt->fetch(PDO::FETCH_ASSOC);

    $categories = $pdo->query("SELECT * FROM Categories")->fetchAll(PDO::FETCH_ASSOC);
}
?>

<?php require_once 'templates/header.php'; ?>

<h2>编辑帖子</h2>
<form method="post">
    标题: <input type="text" name="title" value="<?php echo $post['Title']; ?>" required><br>
    内容: <textarea name="content" required><?php echo $post['Content']; ?></textarea><br>
    分类: 
    <select name="category" required>
        <?php foreach ($categories as $category): ?>
            <option value="<?php echo $category['CategoryID']; ?>" <?php if ($post['CategoryID'] == $category['CategoryID']) echo 'selected'; ?>>
                <?php echo $category['CategoryName']; ?>
            </option>
        <?php endforeach; ?>
    </select><br>
    <button type="submit">更新</button>
</form>

<?php require_once 'templates/footer.php'; ?>
