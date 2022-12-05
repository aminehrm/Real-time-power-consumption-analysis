import os
from kafka import KafkaConsumer, TopicPartition
import json
import locale
import math
import pandas as pd
import time
from datetime import datetime
import time

topic_name = "powerConsumption"
# DescriptiveAnalysisSketch

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='powerConsumption-group'
)

count = 0
df = pd.DataFrame()
# consumer = consumer.subscribe(['PowerConsumption_Zone1'])

while count < 200:
    for msg in consumer:
        count += 1
        data = json.loads(msg.value.decode('utf-8'))
        df_iter = pd.json_normalize(data)
        df = df.append(df_iter)
        print(df['PowerConsumption_Zone1'].astype(float).describe(include='all'))
        time.sleep(5)


'''
    df = df.append(df_iter)
    count        1.00000
    mean     32819.74468
    std              NaN
    min      32819.74468
    25%      32819.74468
    50%      32819.74468
    75%      32819.74468
    max      32819.74468
'''