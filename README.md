# 基于Django的图书管理系统

## 主要功能
* 输入作者名字查询作者
* 点击作者名字显示作者详细信息
* 输入标题查询图书
* 点击图书标题显示图书详细信息
* 查询某个作者所著的全部图书

## 加载初始数据
```shell
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata data.json
```
