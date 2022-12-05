# -*- coding: utf-8 -*-
"""Linear_RegresionSketch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14DN_N9zy50iZ1vzL56ppQbb8DLMxzn1M
"""

!pip install -q pyspark
!pip install -q handyspark

# Commented out IPython magic to ensure Python compatibility.
from pyspark import SparkContext                                     #Importing SparkContext
from pyspark.sql import SparkSession, Window, Row                   # Importing importing methods for creating a cluster
from pyspark.sql import functions as F                              # Importing SQL Functions
from pyspark.sql.functions import col, isnan, when, count           # Importing relevant dataframe functions
from pyspark.sql.functions import *                                 # Importing inbuilt SQL Functions
from pyspark.sql.types import *                                     # Importing SQL types

import matplotlib.pyplot as plt                                     # Popular plotting library
# %matplotlib inline                                                  
import seaborn as sns                                               # Advanced plotting library
from handyspark import *                                            # Helper library to plot graphs

from pyspark.ml.feature import VectorAssembler                      # For processing dataset for ML
from pyspark.ml.regression import LinearRegression                  # Importing mlib linear regression
import warnings                                                     # Importing warning to disable runtime warnings
warnings.filterwarnings("ignore")

"""# **Building a spark app/session**"""

spark = SparkSession.builder.appName("Power_consumption").getOrCreate()

# single cluster information
spark

df = spark.read.options(header='True', inferSchema='True', delimiter=',') \
  .csv("/content/powerconsumption.csv")

type(df)

df.printSchema()

"""Data Post-Processing**
---

- We wll use a **VectorAssembler**.

- VectorAssember from **Spark ML library** is a module that allows to convert **numerical features into a single vector** that is used by the machine learning models.
"""

featureassembler = VectorAssembler(inputCols= ['Temperature','Humidity','WindSpeed','GeneralDiffuseFlows','DiffuseFlows'], outputCol = 'features')

output = featureassembler.transform(df)
output.show()

"""### **Feature Extraction**:"""

final_data = output.select("features", "PowerConsumption_Zone1")
final_data.show()

"""### **Train Test Split**:"""

train_data, test_data = final_data.randomSplit(weights=[0.75,0.25], seed=42)

"""### **Model Initialization and Training**"""

# Initializing a Linear Regression model
model = LinearRegression(featuresCol='features', labelCol='PowerConsumption_Zone1')

model_fit = model.fit(train_data)

model_fit.coefficients

model_fit.intercept

pred = model_fit.evaluate(test_data)
pred.predictions.show()

print('MAE for test set:', pred.meanAbsoluteError)

# Printing MSE
print('MSE for test set:', pred.meanSquaredError)
print('RMSE for test set:', pred.rootMeanSquaredError)
print('R2-Score for test set:', pred.r2)

spark.stop()