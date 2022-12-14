# -*- coding: utf-8 -*-
"""justin.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16XOA3UJwINoqbcsMk6y68ShwO8Ma0ZzM
"""

import os
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

topic_name = 'powerConsumption'
output_topic = 'processedPowerConsumption'


class PowerConsumption:
    
    def get_schema():
        schema = StructType([
            StructField("Temperature", StringType()),
            StructField("Humidity", StringType()),
            StructField("WindSpeed", StringType()),
            StructField("GeneralDiffuseFlows", StringType()),
            StructField("DiffuseFlows", StringType()),
            StructField("PowerConsumption_Zone1", StringType()),
            StructField("PowerConsumption_Zone2", StringType()),
            StructField("PowerConsumption_Zone3", StringType()),
            StructField("PowerConsumption_Zones_AVG", StringType()),
            StructField("Humidity_Classification", StringType()),
            StructField("Datetime", StringType())
        ])
        return schema

    @staticmethod
    def avgPowerConsumption(df):
        df = df.withColumn("PowerConsumption_Zones_AVG", (col("PowerConsumption_Zone1")+col("PowerConsumption_Zone2")+col("PowerConsumption_Zone3"))/3 )
        return df

    def convert_temp(df):
        df = df.withColumn("Temp_fahrenheit", (col("Temperature")*1.8+(32) ))
        return df
    
    @staticmethod
    def AVG_by_Temp(df):
        df = df.groupBy("Temperature").agg(expr("count(PowerConsumption_Zones_AVG) AS summaries"))
        return df
    
    @staticmethod
    def removeDuplicates(df):
        df = df.distinct()
        return df
    
    
if __name__ == "__main__":
    
    # create Spark session
    spark = SparkSession.builder.master('local').getOrCreate()
    #spark.sparkContext.setLogLevel('ERROR')
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "powerConsumption") \
        .option("startingOffsets", "earliest") \
        .load() 
    

    df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
    df = df.withColumn("data", from_json(df.value, PowerConsumption.get_schema())).select("data.*")

    # Preprocess the avg Power Consumption
    df = PowerConsumption.avgPowerConsumption(df)
    # Process the windSpeed Classification
    df = PowerConsumption.convert_temp(df)
    df = PowerConsumption.AVG_by_Temp(df)
    # Remove duplicates
    
    df = PowerConsumption.removeDuplicates(df)
    # Display our data schema structure
    df.printSchema()
    
    assert type(df) == pyspark.sql.dataframe.DataFrame
    row_df = df.select(
        to_json(struct("Datetime")).alias('key'),
        to_json(struct('Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows', 'DiffuseFlows', 'PowerConsumption_Zone1', 'PowerConsumption_Zone2','PowerConsumption_Zone3','PowerConsumption_Zones_AVG','Humidity_Classification','Datetime')).alias("value")
    )
    
    #Writing to console
    #Uncomment if you want to write to console and see the data inside batches every 30 seconds
    #query = row_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)").writeStream.outputMode("append").format("console").trigger(processingTime='30 seconds').start()

    # Writing to Kafka topic processedPowerConsumption
    query = row_df\
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .writeStream\
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("topic", output_topic) \
        .option("checkpointLocation", "checkpoints") \
        .start()

    query.awaitTermination()