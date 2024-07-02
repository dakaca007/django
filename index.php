<?php
// 获取参数
$user_name = $_SERVER['argv'][1]; // 提取第一个参数
$product_id = $_SERVER['argv'][2]; // 提取第二个参数

// 使用参数进行操作
echo "User Name: $user_name";
echo "<br>";
echo "Product ID: $product_id";
echo phpinfo();
