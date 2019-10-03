FROM continuumio/anaconda3:2019.03
RUN apt-get update && apt-get install -y build-essential redis-tools default-libmysqlclient-dev

# Python packages
RUN conda install -c conda-forge passlib flask-login flask-wtf flask-mail flask-user celery
RUN pip install mysqlclient
COPY requirements.txt /cron-job/requirements.txt
RUN pip install -r /cron-job/requirements.txt

COPY . /cron-job
WORKDIR /cron-job

ENTRYPOINT ["/opt/conda/bin/python"]