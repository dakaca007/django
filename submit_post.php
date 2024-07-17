<?php
session_start();
require_once 'database.php';
$userId = $_SESSION['UserID'];
// 获取用户提交的标题和内容
$title = $_POST['title'];
$content = $_POST['content'];
$fenlei=$_POST['fenlei'];


// 插入到数据库中
$pdo = openDatabaseConnection();
$sql = "INSERT INTO Posts (Title, Content, AuthorID,CategoryID) VALUES (?, ?, ?, ?)";
$stmt = $pdo->prepare($sql);
$stmt->execute([$title, $content, $userId, $fenlei]);
$pdo = null; 
// 可以设置一个成功发布的提示信息
$_SESSION['message'] = "成功发布新帖子！";

// 重定向到其他页面，比如首页或者新发表的帖子页面
header("Location: post.php");
exit();
?>
