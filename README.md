mysql数据库放入了docker中

在服务器上部署的时候
确保服务器上mysql在3307端口

1.拉取新的online_judge_web镜像

2.运行镜像 在容器中要运行makemigration 和 migrate


## 本地开发&运行&生产部署：

- 通过`docker start e787`在本地运行`docker`容器`e7870817e7fc`.该容器是mysql容器，utf-8编码。外部访问是3307端口.

- 运行测试代码 `python manage test`

- `pip freeze > requirements.txt` 保存依赖环境

- 本地写好代码推送到 [github仓库](https://github.com/sundyloveme/OnlineJudgerSystem)

- 阿里云容器服务自动构建镜像

- 服务器端拉起镜像，运行部署脚本`run_docker_image_oneline_judge_web.sh`

## 目录
```
.
├── Dockerfile
├── README.md
├── __pycache__
├── account
├── judger_problem
├── manage.py
├── online_judge_server
├── online_judge_web_env # 项目的环境变量
├── requirements.txt
├── run_docker_image_oneline_judge_web.sh # 运行镜像的脚本
├── templates
└── venv
```

## 部署服务器架构
查看架构列表
```shell script
ubuntu@vm10-0-2-2:~$ sudo docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}"
CONTAINER ID        NAMES                 PORTS
70241ca842ac        online_judger_web     
de9f779102de        redis-test            0.0.0.0:6379->6379/tcp
76c430d07a50        docker-mysql-server   33060/tcp, 0.0.0.0:3307->3306/tcp
1bf37f1d6a03        judger_server         0.0.0.0:8080->8080/tcp
```
`online_judger_web` 网站服务主体

`redis-test` redis服务器 主要负责存储**验证码**

`docker-mysql-server` mysql服务器

`judger_server` mysql服务器

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