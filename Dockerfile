FROM python:3.7
WORKDIR /home
COPY . /home
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple  -r requirements.txt
EXPOSE 8383
CMD ["python", "manage.py", "runserver", "0.0.0.0:8383"]