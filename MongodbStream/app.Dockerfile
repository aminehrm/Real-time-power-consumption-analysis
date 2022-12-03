FROM python:3.6
COPY . /var/www/app
WORKDIR /var/www/app
RUN pip install --upgrade pip
RUN pip3 install pymongo
RUN pip3 install kafka-python
EXPOSE 5000
ENTRYPOINT ["python"]