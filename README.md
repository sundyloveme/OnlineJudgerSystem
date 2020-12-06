## 介绍
一个在线代码评测系统（类似于leetcode）。主要使用Python语言和Django框架。

## 技术

`online_judger_web` 网站服务主体。主要使用Django框架

`redis` 主要负责存储验证码

`mysql` 主要存储用户数据和题目数据

`judger_server` 判题服务器。主要负责运行代码并返回运行结果。http协议通信。

`minio` 文件存储服务。主要用于存储题目详情中的图片数据，相当于一个图床。





## 截图

![题目详情](https://ftp.bmp.ovh/imgs/2020/12/0254eb8ae5b99572.png)
![题目列表](https://ftp.bmp.ovh/imgs/2020/12/333604f3cf775f1e.png)
![个人信息页面](https://ftp.bmp.ovh/imgs/2020/12/1c842e3fccefc012.png)
![注册页面](https://ftp.bmp.ovh/imgs/2020/12/49e54191c0dd26dd.png)
![提交代码页面](https://ftp.bmp.ovh/imgs/2020/12/ae1ac67f5463f1e5.png)
![登陆页面](https://ftp.bmp.ovh/imgs/2020/12/c7370eb1ed2931e3.png)
![图床上传功能](https://ftp.bmp.ovh/imgs/2020/12/2b4721c93f9d1d25.png)


## 本地开发&运行&生产部署：

- 通过`docker start e787`在本地运行`docker`容器`e7870817e7fc`.该容器是mysql容器，utf-8编码。外部访问是3307端口.

- 运行测试代码 `python manage test`

- `pip freeze > requirements.txt` 保存依赖环境

- 本地写好代码推送到 [github仓库](https://github.com/sundyloveme/OnlineJudgerSystem)

- 阿里云容器服务自动构建镜像

- 服务器端拉起镜像，运行部署脚本`run_docker_image_oneline_judge_web.sh`


## 其他命令
用开发环境重新配置数据库
`python manage.py makemigrations --settings online_judge_server.settings.dev`
`python manage.py migrate --settings online_judge_server.settings.dev`


## 部署minio

运行minio服务
```shell script
docker pull minio/minio
docker run -p 9000:9000 minio/minio server /data
```

访问 http://127.0.0.1:9000/ 即可 密码和账号都是minioadmin

将数据桶设置为public模式，这样可以以文件名的形式直接访问文件`mc policy set public s3/images`