# 基于Django的图书管理系统

## 功能模块
### 1.用户管理
* 用户登录

### 2.图书管理
* 图书检索
  * 支持按书名检索图书。

### 3.借阅管理
* 借书功能
  * 用户可以通过系统借阅图书。

## 依赖
* Python 3.11
* Django 4.2

## 运行
创建数据库表

```shell
python manage.py migrate
```

启动服务器

```shell
python manage.py runserver
```

运行测试

```shell
python manage.py test
```
