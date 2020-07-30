#!/bin/bash
sudo docker run -it --network host --name online_judger_web --env-file online_judge_web_env  registry.cn-shanghai.aliyuncs.com/sundy-allstar/online_judger_system:0.2
