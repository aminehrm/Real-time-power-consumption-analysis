import os
from kafka import KafkaConsumer
import json
import time
from datetime import datetime
import numpy as np
import pandas
from tabulate import tabulate

headers=["classification", "low","high","normal"]
topic_name = "powerConsumption"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='powerConsumption-group'
)

#This sketch classifier the coming Diffuse flow values and the count the occurence of each category  
counter={
    "low": 0,
    "normal": 0,
    "high": 0
}



for message in consumer:

    mvalue = json.loads(message.value.decode('utf-8'))
    mkey = message.key
    mpart = message.partition
    moffset = message.offset
    print(mvalue)

#Detect outliers in PowerConsumption_Zone1
    temp=float(mvalue['DiffuseFlows'])
    print(temp)
    if 0.2 <= temp <=100 :
        counter['normal']=counter['normal']+1
        #print('normal DiffuseFlows: ',counter['normal'])
    elif 0.2 > temp:
        print('low')
        counter['low']=counter['low']+1
        #print('low DiffuseFlows: ',counter['low'])
    else:
        print('High')
        counter['high']=counter['high']+1
        #print('high DiffuseFlows: ',counter['high'])
    
    data=[['counts', counter['low'], counter['high'], counter['normal']]]
    print(tabulate(data, headers))

    print("-------------------------------------------------------------")


    """ output

    classification      low    high    normal
----------------  -----  ------  --------
counts               29      14        20
-------------------------------------------------------------
{'Datetime': '6/18/2017 1:50', 'Temperature': '20.27', 'Humidity': '86.4', 'WindSpeed': '0.07', 'GeneralDiffuseFlows': '0.066', 'DiffuseFlows': '0.126', 'PowerConsumption_Zone1': '41566.09272', 'PowerConsumption_Zone2': '23938.87734', 'PowerConsumption_Zone3': '26944.98462'}
0.126
low
classification      low    high    normal
----------------  -----  ------  --------
counts               30      14        20
-------------------------------------------------------------
{'Datetime': '6/18/2017 2:00', 'Temperature': '20.25', 'Humidity': '86.5', 'WindSpeed': '0.068', 'GeneralDiffuseFlows': '0.033', 'DiffuseFlows': '0.126', 'PowerConsumption_Zone1': '42201.8543', 'PowerConsumption_Zone2': '24556.34096', 'PowerConsumption_Zone3': '26986.33846'}
0.126
low
classification      low    high    normal
----------------  -----  ------  --------
counts               31      14        20
-------------------------------------------------------------
{'Datetime': '6/18/2017 2:10', 'Temperature': '20.21', 'Humidity': '86.6', 'WindSpeed': '0.065', 'GeneralDiffuseFlows': '0.055', 'DiffuseFlows': '0.159', 'PowerConsumption_Zone1': '41972.98013', 'PowerConsumption_Zone2': '24481.49688', 'PowerConsumption_Zone3': '26602.33846'}
0.159
low
classification      low    high    normal
----------------  -----  ------  --------
counts               32      14        20
-------------------------------------------------------------
{'Datetime': '6/18/2017 2:20', 'Temperature': '20.17', 'Humidity': '86.8', 'WindSpeed': '0.066', 'GeneralDiffuseFlows': '0.033', 'DiffuseFlows': '0.111', 'PowerConsumption_Zone1': '41616.95364', 'PowerConsumption_Zone2': '24227.02703', 'PowerConsumption_Zone3': '26058.83077'}
0.111
low
classification      low    high    normal
----------------  -----  ------  --------
counts               33      14        20
-------------------------------------------------------------
{'Datetime': '6/18/2017 2:30', 'Temperature': '20.12', 'Humidity': '87', 'WindSpeed': '0.065', 'GeneralDiffuseFlows': '0.044', 'DiffuseFlows': '0.133', 'PowerConsumption_Zone1': '40841.3245', 'PowerConsumption_Zone2': '23766.73597', 'PowerConsumption_Zone3': '25704.36923'}
0.133

    """