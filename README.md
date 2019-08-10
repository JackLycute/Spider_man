## Spider_man

**蜘蛛侠数据商城**：小型电商购物网站，基于<code>Python3.5</code>和<code>Django2.0</code>

项目尽量使用Django内部提供的API，后台管理为Django自带的管理系统django-admin。适合接触Django不久之后，作为第一个实战小项目。

## 功能简介：

- 商品浏览：商品的图片，售价，种类，简介以及库存等信息。
- 全文检索：支持对商品种类以及商品名称，简介的检索。
- 登录注册：普通用户与管理人员入口不同。
- 用户中心：支持用户个人信息，收货地址等信息的更新。
- 商品下单：在支付接口和企业资质的支持下可完成商品的下单功能，按照原子事务处理，下单异常则终止此次下单过程。
- 后台管理：基本支持后台简单功能，商品及用户信息的增加，更新与删除，可自定制样式与功能，以及权限管理。
<br>
...

## 预览：
### 首页
![index](https://github.com/JackLycute/Spider_man/blob/master/static/images/index.png)

### 登录
![login](https://github.com/JackLycute/Spider_man/blob/master/static/images/login.png)

### 商品详情
![goods](https://github.com/JackLycute/Spider_man/blob/master/static/images/cart.png)

### 购物车
![cart](https://github.com/JackLycute/Spider_man/blob/master/static/images/account.png)

### 支付
![cart](https://github.com/JackLycute/Spider_man/blob/master/static/images/pay.png)

## 安装：

### 依赖包安装

下载文件进入项目目录之后，使用pip安装依赖包

<code>pip install -Ur requirements.txt</code>

### 数据库配置

数据库默认使用<code>Django</code>项目生成时自动创建的小型数据库<code>sqlite</code>

也可自行连接使用MySQL

### 创建超级用户

终端下执行:

<code>./python manage.py createsuperuser</code>

然后输入相应的超级用户名以及密码，邮箱即可。

### 开始运行

终端下执行:

<code>./python manage.py runserver</code>
 
浏览器打开: <code>http://127.0.0.1</code> 即可进入普通用户入口

浏览器打开: <code>http://127.0.0.1/admin</code> 即可进入超级用户入口


## 补充：

欢迎您对该项目做出任何补充与修改，目前还未的功能：
- 商品的评价功能
- 合适的商品推荐算法
- 用户的邮箱注册
- 一个更多商品数据量的数据库
