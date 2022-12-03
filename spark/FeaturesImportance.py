from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import Normalizer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import StringIndexer, VectorIndexer
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder.appName('Power Consumption Features Importance').getOrCreate()

spark.sparkContext.setLogLevel('ERROR')

data = spark.read.csv('./Dataset/powerconsumption.csv',inferSchema=True,header=True)
data = data.withColumn(
    'Humidity_Classification',
    when(col('Humidity') > 80, lit(3)) #very high
    .when(col('Humidity') > 50, lit(2)) #high
    .otherwise(lit(1)) #low
)
data = data.withColumn("label", data["Humidity_Classification"].cast("integer"))

#print the structure of columns in data
data.printSchema()

# put features into a feature vector column
assembler = VectorAssembler(inputCols=['Temperature','WindSpeed','GeneralDiffuseFlows','DiffuseFlows'], outputCol='features')

final_data = assembler.transform(data)

final_data.show(1)

my_data = final_data.select('features','Humidity_Classification')

#Normalization In Preprocessing
normalizer = Normalizer().setInputCol("features").setOutputCol("nor_features").setP(1.0)
l1NormData = normalizer.transform(my_data)
my_data = l1NormData.select('nor_features','Humidity_Classification')

#split the data
train_data, test_data = my_data.randomSplit([0.7,0.3])

rfc = RandomForestClassifier(labelCol='Humidity_Classification',featuresCol='nor_features')

rfc_model = rfc.fit(train_data)

print ("RandomForestClassifier features importance : ")
print("Feature indexes : Temperature->0, WindSpeed->1, GeneralDiffuseFlows->2, DiffuseFlows->3")
print(rfc_model.featureImportances)

# Stop the session
spark.stop()

"""
Output:

root
 |-- Datetime: string (nullable = true)
 |-- Temperature: double (nullable = true)
 |-- Humidity: double (nullable = true)
 |-- WindSpeed: double (nullable = true)
 |-- GeneralDiffuseFlows: double (nullable = true)
 |-- DiffuseFlows: double (nullable = true)
 |-- PowerConsumption_Zone1: double (nullable = true)
 |-- PowerConsumption_Zone2: double (nullable = true)
 |-- PowerConsumption_Zone3: double (nullable = true)
 |-- Humidity_Classification: integer (nullable = false)
 |-- label: integer (nullable = false)

+-------------+-----------+--------+---------+-------------------+------------+----------------------+----------------------+----------------------+-----------------------+-----+--------------------+
|     Datetime|Temperature|Humidity|WindSpeed|GeneralDiffuseFlows|DiffuseFlows|PowerConsumption_Zone1|PowerConsumption_Zone2|PowerConsumption_Zone3|Humidity_Classification|label|            features|
+-------------+-----------+--------+---------+-------------------+------------+----------------------+----------------------+----------------------+-----------------------+-----+--------------------+
|1/1/2017 0:00|      6.559|    73.8|    0.083|              0.051|       0.119|            34055.6962|           16128.87538|           20240.96386|                      2|    2|[6.559,0.083,0.05...|
+-------------+-----------+--------+---------+-------------------+------------+----------------------+----------------------+----------------------+-----------------------+-----+--------------------+
only showing top 1 row

RandomForestClassifier features importance :
Feature indexes : Temperature->0, WindSpeed->1, GeneralDiffuseFlows->2, DiffuseFlows->3
(4,[0,1,2,3],[0.3591032356763596,0.09632459763944472,0.263648372397217,0.2809237942869787])

As we can see from above Temperature has the highest correlation with Humidity with 0.35
"""