<?php
session_start();
require_once 'includes/database.php';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $pdo = openDatabaseConnection();
    $username = $_POST['username'];
    $password = $_POST['password'];

    $sql = "SELECT * FROM Users WHERE Username = ?";
    $stmt = $pdo->prepare($sql);
    $stmt->execute([$username]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($user && password_verify($password, $user['PasswordHash'])) {
        $_SESSION['UserID'] = $user['UserID'];
        $_SESSION['Username'] = $user['Username'];
        header("Location: index.php");
        exit();
    } else {
        $error = "用户名或密码错误";
    }
}
?>

<?php require_once 'templates/header.php'; ?>

<h2>登录</h2>
<?php if (isset($error)) echo "<p>$error</p>"; ?>
<form method="post">
    用户名: <input type="text" name="username" required><br>
    密码: <input type="password" name="password" required><br>
    <button type="submit">登录</button>
</form>

<?php require_once 'templates/footer.php'; ?>
