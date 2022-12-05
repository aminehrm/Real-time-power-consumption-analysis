import os
from kafka import KafkaConsumer
import json
import locale
import math
from probables import (CountMinSketch)

topic_name = "powerConsumption"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='powerConsumption-group'
)

# use this method for counting all 3 features in batch and overall
cms = CountMinSketch(width=1000, depth=5)

for message in consumer:
    value = json.loads(message.value.decode('utf-8'))
    cms.add('temperature', math.ceil(locale.atof(value['Temperature'])))
    cms.add('humidity', math.ceil(locale.atof(value['Humidity'])))
    cms.add('windSpeed', math.ceil(locale.atof(value['WindSpeed'])))
    cms.add('transaction', 1)

    print("=======================================================================")
    print("temperature")
    print(cms.check('temperature'))

    print("humidity")
    print(cms.check('humidity'))

    print("windSpeed")
    print(cms.check('windSpeed'))
    print("transaction")
    print(cms.check('transaction'))

'''
    =======================================================================
    temperature
    27632
    humidity
    152530
    windSpeed
    4880
    transaction
    3419
'''
