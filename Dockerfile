FROM python:3.7
WORKDIR /online_judge_server

# 方便缓存，下次构建不需要重新下载py依赖
COPY ./requirements.txt .
RUN pip install -i https://mirrors.aliyun.com/pypi/simple  -r requirements.txt

COPY . .
EXPOSE 8383
CMD ["python", "manage.py", "runserver", "0.0.0.0:8383", "--settings", "online_judge_server.settings.dockerenv"]