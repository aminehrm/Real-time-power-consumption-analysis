import os
from kafka import KafkaConsumer
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

topic_name = "powerConsumption"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='powerConsumption-group'
)

token = "7Sw_dO-6aH4GezU-usQFHhG9bWsyv-pUVLetJZj0j3dTwCkYpZrvOeBvQVP6wQ5dG7TH9N3LxF_MMP-AUvvd9g=="
org = "powerConsumption"
bucket = "powerConsumption"

for message in consumer:

    mvalue = json.loads(message.value.decode('utf-8'))
    mkey = message.key
    mpart = message.partition
    moffset = message.offset

    client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    print(message)

    dataPoint = Point("powerConsumptionData")\
        .field("Temperature", float(mvalue['Temperature'])) \
        .field("Humidity", float(mvalue['Humidity'])) \
        .field('WindSpeed', float(mvalue['WindSpeed'])) \
        .field('GeneralDiffuseFlows', float(mvalue['GeneralDiffuseFlows'])) \
        .field('DiffuseFlows', float(mvalue['DiffuseFlows'])) \
        .field('PowerConsumption_Zone1', float(mvalue['PowerConsumption_Zone1'])) \
        .field('PowerConsumption_Zone2', float(mvalue['PowerConsumption_Zone2'])) \
        .field('PowerConsumption_Zone3', float(mvalue['PowerConsumption_Zone3'])) \
        .time(mvalue['Datetime'])

    print(dataPoint)

    write_api.write(bucket=bucket, record=dataPoint)
    
    print('Writing was successful to Kafka topic');