USE
跟着<Flask Web 开发实战>作者李辉greyli学习的 todoism 待办事项,里面有web api
使用就是命令行输入:  flask run
使用网址是你电脑 局域网IP地址:5000(例如 192.168.1.10:5000), 因为我把host 设置成了0.0.0.0
打开网址后先登陆, 可以直接使用测试随机用户名密码, 随机生成, 点击登陆前先把 用户名与密码复制粘贴保存好,下面有一步骤是要填写的

API
api要先安装 HTTPie工具(pip install httpie)

然后在命令行先取到token令牌: http --form xxx.xxx.xxx.xxx:5000/oauth/token grant_type=password usrname=xxxx password=xxxx
正常的情况会显示 
{
    "access_token": " eyJhbGciOiJIUzUxMiIsImlhd6MTYyODkyNTIyMiwiZXhwIjoxNjI4OTI4ODIyfQ.eyJpZCI6MjB9.uCysoAdkWye6j3PSwGzMM9nv8dmbQQWRCkyhD6nUuf4A5zKbBQkXOJ4JL_1aWWRI0zyxtJT7Uy1ObhThTBwq4w",
    "expires_in": 3600,
    "token_type": "Bearer"
}

再把access_token的值包括前后的引号都要复制下来类似这样, 令牌1小时内有效   "eyJhbGciOiJIUzUxMiIsImlhd6MTYyODkyNTIyMiwiZXhwIjoxNjI4OTI4ODIyfQ.eyJpZCI6MjB9.uCysoAdkWye6j3PSwGzMM9nv8dmbQQWRCkyhD6nUuf4A5zKbBQkXOJ4JL_1aWWRI0zyxtJT7Uy1ObhThTBwq4w"

再使用命令获取user json数据,下面是范例, 令牌请换成你自己获取刚的token,  
http xxx.xxx.xxx.xxx:5000/api/v1/user  Authorization:"Bearer eyJhbGciOiJIUzUxMiIsImlhdCI6MTYyODkyNTIyMiZXhwIjoxNjI4OTI4ODIyfQ.eyJpZCI6MjB9.uCysoAdkWye6j3PSwGzMM9nv8dmbQQWRCkyhD6nUuf4A5zKbBQkXOJ4JL_1aWWRI0zyxtJT7Uy1ObhThTBwq4w"

还可以获取user 的所有待办事项items数据
http xxx.xxx.xxx.xxx:5000/api/v1/user/items  Authorization:"Bearer eyJhbGciOiJIUzUxMiIsImlhdCI6MTYyODkyNTIyMiZXhwIjoxNjI4OTI4ODIyfQ.eyJpZCI6MjB9.uCysoAdkWye6j3PSwGzMM9nv8dmbQQWRCkyhD6nUuf4A5zKbBQkXOJ4JL_1aWWRI0zyxtJT7Uy1ObhThTBwq4w"

或者items中active未完成的items数据
http xxx.xxx.xxx.xxx:5000/api/v1/user/items/active  Authorization:"Bearer eyJhbGciOiJIUzUxMiIsImlhdCI6MTYyODkyNTIyMiZXhwIjoxNjI4OTI4ODIyfQ.eyJpZCI6MjB9.uCysoAdkWye6j3PSwGzMM9nv8dmbQQWRCkyhD6nUuf4A5zKbBQkXOJ4JL_1aWWRI0zyxtJT7Uy1ObhThTBwq4w"

items中completed已完成数据
http xxx.xxx.xxx.xxx:5000/api/v1/user/completed  Authorization:"Bearer eyJhbGciOiJIUzUxMiIsImlhdCI6MTYyODkyNTIyMiZXhwIjoxNjI4OTI4ODIyfQ.eyJpZCI6MjB9.uCysoAdkWye6j3PSwGzMM9nv8dmbQQWRCkyhD6nUuf4A5zKbBQkXOJ4JL_1aWWRI0zyxtJT7Uy1ObhThTBwq4w"
