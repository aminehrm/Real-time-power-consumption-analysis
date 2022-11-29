import os
from kafka import KafkaConsumer
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime


topic_name = "processedPowerConsumption"
token = "fNpbc0raV6ir31D_r-MttmiFNOqarG4_M6SSNSYNUB41XfzpHt8oQ3n72_eafJ8AzpUuwfOtasYqtNYNNnjIgw=="
org = "powerConsumption"
bucket = "powerConsumption"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='processedPowerConsumption-group'
)

for message in consumer:

    print("Reading data from consumer ...")
    
    mvalue = json.loads(message.value.decode('utf-8'))
    mkey = message.key
    mpart = message.partition
    moffset = message.offset

    client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    print(message)

    dataPoint = Point("processedPowerConsumptionData")\
        .field("Temperature", float(mvalue['Temperature'])) \
        .field("Humidity", float(mvalue['Humidity'])) \
        .field('WindSpeed', float(mvalue['WindSpeed'])) \
        .field('GeneralDiffuseFlows', float(mvalue['GeneralDiffuseFlows'])) \
        .field('DiffuseFlows', float(mvalue['DiffuseFlows'])) \
        .field('PowerConsumption_Zone1', float(mvalue['PowerConsumption_Zone1'])) \
        .field('PowerConsumption_Zone2', float(mvalue['PowerConsumption_Zone2'])) \
        .field('PowerConsumption_Zone3', float(mvalue['PowerConsumption_Zone3'])) \
        .field('PowerConsumption_Zones_AVG', float(mvalue['PowerConsumption_Zones_AVG'])) \
        .field('Humidity_Classification', float(mvalue['Humidity_Classification'])) \
        .time(datetime.strptime(mvalue['Datetime'], '%m/%d/%Y %H:%M')) 


    print(dataPoint)

    write_api.write(bucket=bucket, record=dataPoint)
    
    print('Writing was successful to processedPowerConsumption topic');