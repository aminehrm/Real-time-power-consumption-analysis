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
for i in range(5):
    if not( isinstance(df.select(i).take(1)[0][0], six.string_types)):
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
print("Coefficients: " + str(lr_model.coefficients))

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