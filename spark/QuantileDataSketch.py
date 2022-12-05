from pyspark.sql import SparkSession
import pyspark.sql.functions as f


# create Spark session
spark = SparkSession.builder.master('local').getOrCreate()


#df = spark.read.csv('./Dataset/powerconsumption.csv',inferSchema=True,header=True)

df = spark.read.format("csv").options(header='true', inferschema='true').load("./Dataset/powerconsumption.csv")

#Print Schema in a tree format
df.printSchema()

#showing only top 5 rows
df.show(5)

#summarie of the data
df.describe().show(5, False)

#percentile estimation function
df.selectExpr("percentile(PowerConsumption_Zone2, 0.95) percentile", "approx_percentile(PowerConsumption_Zone2, 0.95) approx_percentile")
df.show()

#accumulate quantile summaries for each time interval and estimate quantile values over specific intervals
summaries = df.groupBy(f.window("Datetime", "1 week")).agg(f.expr("approx_percentile_accumulate(PowerConsumption_Zone2) AS summaries"))
summaries.show(3, 50)

# Correct percentile of the `PowerConsumption_Zone2` column
df.where("Date between '2017-01-01' and '2017-02-01'").selectExpr("percentile(PowerConsumption_Zone2, 0.95) correct")
df.show()

# Estimated percentile of the `PowerConsumption_Zone2` column
df = summaries.where("window.start > '2017-01-01' and window.end < '2017-02-01'").selectExpr("approx_percentile_combine(summaries) merged")
df.selectExpr("approx_percentile_estimate(merged, 0.95) percentile")
df.show()

#pmf estimate
df.selectExpr("approx_pmf_estimate(merged, 4) pmf")
df.show(1, False)

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

+-------------+-----------+--------+---------+-------------------+------------+----------------------+----------------------+----------------------+
|     Datetime|Temperature|Humidity|WindSpeed|GeneralDiffuseFlows|DiffuseFlows|PowerConsumption_Zone1|PowerConsumption_Zone2|PowerConsumption_Zone3|
+-------------+-----------+--------+---------+-------------------+------------+----------------------+----------------------+----------------------+
|1/1/2017 0:00|      6.559|    73.8|    0.083|              0.051|       0.119|            34055.6962|           16128.87538|           20240.96386|
|1/1/2017 0:10|      6.414|    74.5|    0.083|               0.07|       0.085|           29814.68354|           19375.07599|           20131.08434|
|1/1/2017 0:20|      6.313|    74.5|     0.08|              0.062|         0.1|           29128.10127|           19006.68693|           19668.43373|
|1/1/2017 0:30|      6.121|    75.0|    0.083|              0.091|       0.096|           28228.86076|           18361.09422|           18899.27711|
|1/1/2017 0:40|      5.921|    75.7|    0.081|              0.048|       0.085|            27335.6962|           17872.34043|           18442.40964|
+-------------+-----------+--------+---------+-------------------+------------+----------------------+----------------------+----------------------+
only showing top 5 rows

+-------+-------------+------------------+------------------+------------------+-------------------+------------------+----------------------+----------------------+----------------------+
|summary|Datetime     |Temperature       |Humidity          |WindSpeed         |GeneralDiffuseFlows|DiffuseFlows      |PowerConsumption_Zone1|PowerConsumption_Zone2|PowerConsumption_Zone3|
+-------+-------------+------------------+------------------+------------------+-------------------+------------------+----------------------+----------------------+----------------------+
|count  |52416        |52416             |52416             |52416             |52416              |52416             |52416                 |52416                 |52416                 |
|mean   |null         |18.810023962149035|68.25951846764387 |1.9594888583639214|182.69661376298353 |75.02802192078356 |32344.970563586106    |21042.509082321845    |17835.406218376575    |
|stddev |null         |5.8154758389084655|15.551177174321259|2.348861953883841 |264.40095966802545 |124.21094932969427|7130.562564198572     |5201.465892178912     |6622.165099245538     |
|min    |1/1/2017 0:00|3.247             |11.34             |0.05              |0.004              |0.011             |13895.6962            |8560.081466           |5935.17407            |
|max    |9/9/2017 9:50|40.01             |94.8              |6.483             |1163.0             |936.0             |52204.39512           |37408.86076           |47598.32636           |
+-------+-------------+------------------+------------------+------------------+-------------------+------------------+----------------------+----------------------+----------------------+


'''