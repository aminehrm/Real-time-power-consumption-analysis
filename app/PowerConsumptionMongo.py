import os
import json
from kafka import KafkaConsumer
from pymongo import MongoClient, errors
import time
from datetime import datetime

topic_name = "powerConsumption"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['kafka:29092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='powerConsumption-group'
)


# global variables for MongoDB host (default port is 27017)
DOMAIN = 'mongodb'
PORT = 27017



config = {
    "username": "admin",
    "password": "admin",
    "server": "mongodb",
}


try:
    # try to instantiate a client instance
    connector = "mongodb://{}:{}@{}".format(config["username"], config["password"], config["server"])
    print(connector)
    client = MongoClient(connector)
    mydb = client["powerConsumption"]
    mycol = mydb["powerConsumptionData"] 
    print ("server version:", client.server_info()["version"])

    for message in consumer:

        mvalue = json.loads(message.value.decode('utf-8'))
        x = mycol.insert_one(mvalue)
        print(x.inserted_id)         
        print('Writing was successful to Kafka topic');

except errors.ServerSelectionTimeoutError as err:
    # catch pymongo.errors.ServerSelectionTimeoutError
    print ("pymongo ERROR:", err)



