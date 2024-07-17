<?php
require_once 'database.php';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $pdo = openDatabaseConnection();
    $username = $_POST['username'];
    $password = password_hash($_POST['password'], PASSWORD_BCRYPT);
    $email = $_POST['email'];

    $sql = "INSERT INTO Users (Username, PasswordHash, Email) VALUES (?, ?, ?)";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$username, $password, $email]);

    header("Location: login.php");
    exit();
}
?>

<?php require_once 'templates/header.php'; ?>

<h2>注册</h2>
<form method="post">
    用户名: <input type="text" name="username" required><br>
    密码: <input type="password" name="password" required><br>
    邮箱: <input type="email" name="email" required><br>
    <button type="submit">注册</button>
</form>

<?php require_once 'templates/footer.php'; ?>
