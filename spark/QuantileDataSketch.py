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

#percentile estimation function and approx_percentile_ex to estimate percentiles in a theoretically-meageable and very compact way
df.selectExpr("percentile(PowerConsumption_Zone2, 0.95) percentile", "approx_percentile(PowerConsumption_Zone2, 0.95) approx_percentile", "approx_percentile_ex(PowerConsumption_Zone2, 0.95) approx_percentile_ex")
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