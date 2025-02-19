-- 创建一个新的数据库
CREATE DATABASE IF NOT EXISTS mydatabase;

-- 创建一个新用户并授予权限
CREATE USER 'myuser'@'%' IDENTIFIED BY 'mypassword';
GRANT ALL PRIVILEGES ON mydatabase.* TO 'myuser'@'%';
FLUSH PRIVILEGES;