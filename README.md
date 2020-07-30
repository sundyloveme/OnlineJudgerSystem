mysql数据库放入了docker中

在服务器上部署的时候
确保服务器上mysql在3307端口

1.拉取新的online_judge_web镜像

2.运行镜像 在容器中要运行makemigration 和 migrate


## 本地开发&运行&生产部署：

- 通过`docker start e787`在本地运行`docker`容器`e7870817e7fc`.该容器是mysql容器，utf-8编码。外部访问是3307端口.

- 运行测试代码 `python manage test`

- 本地写好代码推送到 [github仓库](https://github.com/sundyloveme/OnlineJudgerSystem)

- 阿里云容器服务自动构建镜像

- 服务器端拉起镜像，运行部署脚本`run_docker_image_oneline_judge_web.sh`

## 目录
```shell script
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