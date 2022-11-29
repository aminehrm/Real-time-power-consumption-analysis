from kafka import KafkaConsumer, KafkaProducer

import json

from json import loads

from csv import DictReader

import time



# Set up for Kafka Producer

bootstrap_servers = ['localhost:9092']

topicname = 'powerConsumption'

producer = KafkaProducer(bootstrap_servers = bootstrap_servers)

producer = KafkaProducer()


with open('./Dataset/powerconsumption.csv','r') as new_obj:

    csv_dict_reader = DictReader(new_obj)
    
    index = 0

    for row in csv_dict_reader:

        producer.send(topicname, json.dumps(row).encode('utf-8'))
        
        print("Data sent successfully",row)
        
        index += 1
        
        if (index % 20) == 0:
            time.sleep(10)
