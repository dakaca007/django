<?php
session_start();
require_once 'database.php';

if (!isset($_SESSION['UserID'])) {
    header("Location: login.php");
    exit();
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $pdo = openDatabaseConnection();
    $title = $_POST['title'];
    $content = $_POST['content'];
    $authorID = $_SESSION['UserID'];
    $categoryID = $_POST['category'];

    $sql = "INSERT INTO Posts (Title, Content, AuthorID, CategoryID) VALUES (?, ?, ?, ?)";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$title, $content, $authorID, $categoryID]);

    header("Location: index.php");
    exit();
}

$pdo = openDatabaseConnection();
$categories = $pdo->query("SELECT * FROM Categories")->fetchAll(PDO::FETCH_ASSOC);
?>

<?php require_once 'templates/header.php'; ?>

<h2>发帖</h2>
<form method="post">
    标题: <input type="text" name="title" required><br>
    内容: <textarea name="content" required></textarea><br>
    分类: 
    <select name="category" required>
        <?php foreach ($categories as $category): ?>
            <option value="<?php echo $category['CategoryID']; ?>"><?php echo $category['CategoryName']; ?></option>
        <?php endforeach; ?>
    </select><br>
    <button type="submit">发帖</button>
</form>

<?php require_once 'templates/footer.php'; ?>
