import os
from kafka import KafkaConsumer
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
from datetime import datetime
import numpy as np


topic_name = "powerConsumption"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='powerConsumption-group'
)

nb_max=0
data=list()
prev_avg_std=[0,0]

#calculate the avererage and Std of n previuos values

def average(data, n,i,prev_std,prev_avg,prev_avg_std):
    if len(data)==n:
        avg= sum(data)/len(data)
        st=np.std(data)
        prev_std=st
        prev_avg=avg
        prev_avg_std.clear()
        prev_avg_std.append(prev_avg)
        prev_avg_std.append(prev_std)
        data.clear()
    else:
        prev_avg=prev_avg_std[0]
        prev_std=prev_avg_std[1]
        data.append(i)
        avg=404 
        st=404   
    return [avg,st,prev_avg,prev_std]



for message in consumer:
    n=5
    prev_avg=0
    prev_std=0
    mvalue = json.loads(message.value.decode('utf-8'))
    mkey = message.key
    mpart = message.partition
    moffset = message.offset
    #print(mvalue)

#Detect outliers in PowerConsumption_Zone1
    temp=float(mvalue['PowerConsumption_Zone1'])
    rs=average(data,n,temp,prev_avg,prev_std,prev_avg_std) 
    if rs[0]==404:   
        print("previous std is :",rs[2])
        print("previous avg is :",rs[3])
    else:
        print("New avg is :",rs[0])
        print("New std is :",rs[1])
        print("previous std is :",rs[2])
        print("previous avg is :",rs[3])
    
     
#The range of a non-outlier is from (prev_avg - std) to (prev_avg + std).
    if not (rs[3]-rs[2]) <= temp <= (rs[3]+rs[2]):
            print("********************* This is an outlier ************")
            print(mvalue)
            print("*****************************************************")
    else :
            print("no outlier detected at the moment")


"""

*****************************************************
previous std is : 37732.030139999995
previous avg is : 2392.137874175271
********************* This is an outlier ************
{'Datetime': '4/25/2017 19:40', 'Temperature': '17.7', 'Humidity': '67.4', 'WindSpeed': '0.081', 'GeneralDiffuseFlows': '33.84', 'DiffuseFlows': '28.63', 'PowerConsumption_Zone1': '46551.21636', 'PowerConsumption_Zone2': '23865.58045', 'PowerConsumption_Zone3': '28561.45455'}
*****************************************************
previous std is : 37732.030139999995
previous avg is : 2392.137874175271
********************* This is an outlier ************
{'Datetime': '4/25/2017 19:50', 'Temperature': '17.49', 'Humidity': '64.63', 'WindSpeed': '0.081', 'GeneralDiffuseFlows': '11.03', 'DiffuseFlows': '8.96', 'PowerConsumption_Zone1': '45422.77718', 'PowerConsumption_Zone2': '24639.10387', 'PowerConsumption_Zone3': '28695.27273'}
*****************************************************
previous std is : 37732.030139999995
previous avg is : 2392.137874175271
********************* This is an outlier ************
{'Datetime': '4/25/2017 20:00', 'Temperature': '17.29', 'Humidity': '65.1', 'WindSpeed': '0.082', 'GeneralDiffuseFlows': '3.442', 'DiffuseFlows': '3.003', 'PowerConsumption_Zone1': '45658.38536', 'PowerConsumption_Zone2': '24708.75764', 'PowerConsumption_Zone3': '28567.27273'}
*****************************************************
New avg is : 46075.03982600001
New std is : 531.2596845744517
previous std is : 46075.03982600001
previous avg is : 531.2596845744517
no outlier detected at the moment


"""