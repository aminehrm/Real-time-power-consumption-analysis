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
            StructField("WindSpeed_Classification", StringType()),
            StructField("Datetime", StringType())
        ])
        return schema

    @staticmethod
    def avgPowerConsumption(df):
        df = df.withColumn("PowerConsumption_Zones_AVG", (col("PowerConsumption_Zone1")+col("PowerConsumption_Zone2")+col("PowerConsumption_Zone3"))/3 )
        return df
    
    @staticmethod
    def humidityClassification(df):
        df = df.withColumn(
            'Humidity_Classification',
            when(col('Humidity') > 80, lit('3')) #very high
            .when(col('Humidity') > 50, lit('2')) #high
            .otherwise(lit('1')) #low
        )
        return df
    
    @staticmethod
    def removeDuplicates(df):
        df = df.distinct()
        return df
    
    @staticmethod
    def windSpeedClassification(df):
        df = df.withColumn(
            'WindSpeed_Classification',
             when(col('WindSpeed') > 3.5, lit('3')) # high
            .when(col('WindSpeed') < 2, lit('1')) # low
            .otherwise(lit('2')) # medium
        )
        return df

    @staticmethod
    def filterSketch(df):
        df = df.filter(col('Temperature') > 0).show(truncate=False)
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
    df = PowerConsumption.humidityClassification(df)
    # Remove duplicates
    df = PowerConsumption.removeDuplicates(df)
    # Wind speed classification
    df = PowerConsumption.windSpeedClassification(df)
    # get data when temperature greater than 0 
    df = PowerConsumption.filterSketch(df)
    # Display our data schema structure
    df.printSchema()
    
    assert type(df) == pyspark.sql.dataframe.DataFrame
    row_df = df.select(
        to_json(struct("Datetime")).alias('key'),
        to_json(struct('Temperature', 'Humidity', 'WindSpeed', 'GeneralDiffuseFlows', 'DiffuseFlows', 'PowerConsumption_Zone1', 'PowerConsumption_Zone2','PowerConsumption_Zone3','PowerConsumption_Zones_AVG','Humidity_Classification', 'WindSpeed_Classification','Datetime')).alias("value")
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