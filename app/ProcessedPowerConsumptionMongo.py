import os
import json
from kafka import KafkaConsumer
from pymongo import MongoClient, errors
import time
from datetime import datetime

topic_name = "processedPowerConsumption"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=['kafka:29092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='processedPowerConsumption-group'
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
    mydb = client["ProcessedpowerConsumption"]
    mycol = mydb["ProcessedpowerConsumptionData"] 
    print ("server version:", client.server_info()["version"])
    database_names = client.list_database_names()

    for message in consumer:
        print("Reading data from consumer ...")
        mvalue = json.loads(message.value.decode('utf-8'))
        x = mycol.insert_one(mvalue)
        print(x.inserted_id)         
        print('Writing was successful to Kafka topic');

except errors.ServerSelectionTimeoutError as err:
    # catch pymongo.errors.ServerSelectionTimeoutError
    print ("pymongo ERROR:", err)

