FROM python:3.7
ADD entrypoint.sh loadStream.py processStream.py Dataset/* ./ 
COPY entrypoint.sh loadStream.py processStream.py Dataset/* ./
RUN pip install kafka-python
ENTRYPOINT ["bash", "entrypoint.sh"]
