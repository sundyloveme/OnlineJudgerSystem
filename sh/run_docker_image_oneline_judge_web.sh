#!/bin/bash
echo "拉取新镜像"
sudo docker pull registry.cn-shanghai.aliyuncs.com/sundy-allstar/online_judger_system:0.2

echo "停止运行中的容器"
sudo docker stop online_judger_web

echo "删除容器"
sudo docker rm online_judger_web

echo "运行新的容器"
sudo docker run -itd --network host --name online_judger_web --env-file online_judge_web_env \
        registry.cn-shanghai.aliyuncs.com/sundy-allstar/online_judger_system:0.2

echo "在新容器内重构数据库结构"
sudo docker exec  -it online_judger_web python manage.py migrate

echo "运行单元测试"
sudo docker exec  -it online_judger_web python manage.py test --settings online_judge_server.settings.dev

echo "运行服务器"
sudo docker exec  -it online_judger_web python manage.py runserver 0.0.0.0:8383