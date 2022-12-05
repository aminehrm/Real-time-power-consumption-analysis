from pyspark.sql import SparkSession
import six
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.regression import DecisionTreeRegressor

#build the session
spark = SparkSession.builder.master('local').getOrCreate()

df = spark.read.format('csv').options(header='true', inferschema='true').load('./Dataset/powerconsumption.csv')

#Print Schema in a tree format
df.cache()
df.printSchema()

#perform descriptive analytics
df.describe().toPandas().transpose()

#find correlation between independent variables and target variable
for i in range(6):
    if not( isinstance(df.select(i+1).take(1)[0][0], six.string_types)):
        print( "Correlation to PowerConsumption_Zone3 for ", i, df.stat.corr('PowerConsumption_Zone3',i))

#prepare data. we need two columns — features and label
vectorAssembler = VectorAssembler(inputCols = ['Temperature','Humidity','WindSpeed','GeneralDiffuseFlows','DiffuseFlows'], outputCol = 'features')
vec_df = vectorAssembler.transform(df)
vec_df = vec_df.select(['features', 'PowerConsumption_Zone3'])
vec_df.show(3)

#split between train and test
splits = vec_df.randomSplit([0.7, 0.3])
train_df = splits[0]
test_df = splits[1]

#Linear Regression
lr = LinearRegression(featuresCol='features', labelCol='PowerConsumption_Zone3', maxIter=10, regParam=0.3, elasticNetParam=0.8)
lr_model = lr.fit(train_df)
print("Coefficients: " + str(lr_model.coefficients)) # the coefficients of the model 

#Summarize the model over training data and print some metrics
trainingSummary = lr_model.summary
#root mean square error metric and r2
print("r2: %f" % trainingSummary.r2)
print("RMSE: %f" % trainingSummary.rootMeanSquaredError)


#show some predictions on the test data
lr_predictions = lr_model.transform(test_df)
lr_predictions.select("prediction", "PowerConsumption_Zone3", "features")
lr_predictions.show(10)

#Evaluation on the test data
lr_evaluator = RegressionEvaluator(predictionCol="prediction", labelCol="PowerConsumption_Zone3", metricName="r2")
print("R Squared (R2) on test data = %g" % lr_evaluator.evaluate(lr_predictions))
test_result = lr_model.evaluate(test_df)
print("from Linear Regression:")
print("Root Mean Squared Error (RMSE) on test data = %g" % test_result.rootMeanSquaredError)


#Decision tree regression
dt = DecisionTreeRegressor(featuresCol='features', labelCol='PowerConsumption_Zone3')
dt_model = dt.fit(train_df)
dt_predictions = dt_model.transform(test_df)

#Evaluation on test
dt_evaluator = RegressionEvaluator(labelCol="PowerConsumption_Zone3", predictionCol="prediction", metricName="rmse")
rmse = dt_evaluator.evaluate(dt_predictions)
print("from Decision tree:")
print("Root Mean Squared Error (RMSE) on test data = %g" % rmse)

# now we can compare between LR and DTR

spark.stop()

#Output

'''
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

+--------------------+----------------------+
|            features|PowerConsumption_Zone3|
+--------------------+----------------------+
|[6.559,73.8,0.083...|           20240.96386|
|[6.414,74.5,0.083...|           20131.08434|
|[6.313,74.5,0.08,...|           19668.43373|
+--------------------+----------------------+
only showing top 3 rows

Coefficients: [612.3337364807386,-34.565550434547475,107.90911676872065,-5.011481835457583,-2.6817557972040533]

r2: 0.280932
RMSE: 5624.790089

+--------------------+----------------------+-----------------+
|            features|PowerConsumption_Zone3|       prediction|
+--------------------+----------------------+-----------------+
|[3.541,80.8,0.085...|           14232.28916|8972.525446913762|
|[3.662,79.9,0.085...|           13948.91566|9077.421994216998|
|[3.681,82.7,0.086...|           14480.96386|8992.399174788054|
|[3.706,79.7,0.085...|           13231.80723|9111.311160350177|
|[3.835,78.1,0.805...|           11635.66265|9261.063384445633|
|[3.873,77.9,4.915...|           11843.85542|9548.511297408313|
|[3.961,79.3,0.088...|           12144.57831| 9281.75154365012|
|[3.992,76.7,0.084...|           11225.06024| 9378.58566359677|
|[4.045,76.7,0.245...|           10999.51807|9438.245029154314|
|[4.058,76.4,4.92,...|           12676.62651|9226.947048830914|
+--------------------+----------------------+-----------------+
only showing top 10 rows

R Squared (R2) on test data = 0.282394

from Linear Regression:
Root Mean Squared Error (RMSE) on test data = 5587.64

from Decision tree:
Root Mean Squared Error (RMSE) on test data = 4843.97
'''