FROM python:3.7
WORKDIR /home
COPY . /home
RUN pip install -i http://mirrors.aliyun.com/pypi/simple/  -r requirements.txt
EXPOSE 8383
CMD ["python", "manage.py", "runserver", "0.0.0.0:8383"]