FROM jupyter/pyspark-notebook
COPY . .
RUN pip install influxdb-client
RUN python3 -m pip install influxdb-client
RUN pip install numpy