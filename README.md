# 基于Django的图书管理系统

## 依赖版本
* Python 3.8
* Django 3.2.5

## 主要功能
### 读者
* [x] 注册、登录
* [x] 根据书名查询图书
  * [ ] 分页显示
* [x] 查看图书详细信息
* [ ] 预约、续借
* [ ] 查询自己的基本资料、借阅图书情况

### 管理员
* [x] 登录
* [ ] 图书管理：增删改查
* [ ] 读者管理：增删改查
* [ ] 借出、归还
* [ ] 查询读者借阅次数

## 加载初始数据
```shell
python manage.py migrate
python manage.py loaddata data.json
```
