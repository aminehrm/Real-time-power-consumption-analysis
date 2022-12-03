from __future__ import print_function
from pyspark.ml.feature import Normalizer
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.sql import SparkSession

if __name__ == "__main__":

    # Create a SparkSession 
    spark = SparkSession.builder.master("local").appName("PowerConsumption_Zone3_Predection").getOrCreate()
    spark.sparkContext.setLogLevel('ERROR')
    
    #Reading csv file in pyspark
    data = spark.read.csv('./Dataset/powerconsumption.csv',inferSchema=True,
                         header=True)
    #Schema of Dataset
    data.printSchema()
    
    # put features into a feature vector column
    assembler = VectorAssembler(inputCols=['Temperature','Humidity','WindSpeed','GeneralDiffuseFlows','DiffuseFlows','PowerConsumption_Zone1','PowerConsumption_Zone2'], outputCol='features')
    data_frame = assembler.transform(data)
    spark_data_frame = data_frame.select('features','PowerConsumption_Zone3')
    
    #Normalization In Preprocessing
    normalizer = Normalizer().setInputCol("features").setOutputCol("nor_features").setP(1.0)
    l1NormData = normalizer.transform(spark_data_frame)
    spark_data_frame_norm = l1NormData.select('nor_features','PowerConsumption_Zone3')

    # Split the data into train and test sets
    train_data, test_data = spark_data_frame_norm.randomSplit([0.7,0.3])
    
    #Calling Linear Regression Algorithm from 'pyspark.ml.regression'
    reg = LinearRegression(labelCol='PowerConsumption_Zone3',featuresCol='nor_features', predictionCol='pred',  maxIter=10, regParam=0.3, elasticNetParam=0.8)
    
    #Fittig Train Data to the Model
    model =  reg.fit(train_data)
    
    #Predicting on the Test Data
    predictions = model.transform(test_data)
    predictions.show()
        
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
 
 
+--------------------+----------------------+------------------+
|        nor_features|PowerConsumption_Zone3|              pred|
+--------------------+----------------------+------------------+
|[8.93308144530724...|           14226.50602|11586.001518833176|
|[9.01876628508005...|           14585.06024|14283.686233935574|
|[9.30654656379479...|           15226.98795|13937.757546497494|
|[9.97397253888927...|           11225.06024| 14121.59554497393|
|[1.01397985282154...|           7606.242497|11020.523687557612|
|[1.03943702566709...|           9594.237695|10148.266002759125|
|[1.04696835519391...|            14613.9759|16785.277935485512|
|[1.05661607801765...|           9853.541417|10212.279626802636|
|[1.05677600131588...|            9963.02521|10555.576557353663|
|[1.05860709605386...|           10999.51807|12775.056682074337|
|[1.06757362494630...|           13769.63855|13385.694864768466|
|[1.06838124655303...|           8286.194478|13259.059102153526|
|[1.07787317691606...|           10883.85542| 13585.64315413634|
|[1.10917045056600...|           9104.441777|12108.318361552114|
|[1.11326152595349...|           14035.66265|17180.705082871653|
|[1.11849249297971...|           7404.561825| 9472.552142641744|
|[1.14600069301710...|           24769.15663| 23289.97371214839|
|[1.15050248284813...|           10596.87875|10984.008352541605|
|[1.15190147506546...|           7992.316927|11388.054122515916|
|[1.16264862622872...|            14382.6506|12769.324572386982|
+--------------------+----------------------+------------------+
only showing top 20 rows

"""
