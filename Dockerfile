FROM python:2.7
CMD ["./wait-for-it.sh", "redis:6379", "--", "python", "manage.py", "runserver", "0.0.0.0:80" ]
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
