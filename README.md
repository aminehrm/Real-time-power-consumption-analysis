# Real-time-power-consumption-analysis-
With the electricity consumption being so crucial worldwide, the idea is to study the impact on energy consumption. The dataset is exhaustive in its demonstration of energy consumption of the Tétouan city in Morocco. The distribution network is powered by 3 Zone stations.The data consists of 52,416 observations of energy consumption on a 10-minute window. Every observation is described by 9 feature columns.<br />
<br />

## Project architecture diagram

![architecture](https://user-images.githubusercontent.com/17914107/201059480-6cc7c7a5-e341-4e85-84c0-1d6253925cad.png)

<br />

## Steps to run the project (with InfluxDB) 
<br />
1- Run "docker-compose up" in root direcotry<br />
2- Generate new Influxdb credentials (api token) and replace it in .env , telegraf/teleraf.conf and ProcessedPowerConsumptionConsumer.py and PowerConsumptionConsumer.py<br />
3- Run "docker-compose down" then "docker-compose up" <br />
4- Go to kafka folder and run the procedure "python3 Procedure.py" <br /> 
5- run "docker exec -it [Spark containerID]" to be inside SPARK container then run "spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 DataPreprocessingSpark.py"<br /> 
6-  Go to kafka folder again and run the consumer "python3 ProcessedPowerConsumptionConsumer.py" (if you want to send data to influxdb without the preprocessing run "python3 PowerConsumptionConsumer.py") <br /> 
7- Create a new Influxdb data source in Grafana to vizualize the results<br />

Note : All sketches are located in spark folder, In order to run any skitech go inside spark docker container then run spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 <sketch_name.py>"

## Grafana http://localhost:3000/ ( admin - admin )<br />

![Grafana Power consumption analysis](https://user-images.githubusercontent.com/17914107/205452043-caf37019-f17c-4d46-8858-b33cc54d5a9c.png)

<br />

## Influxdb http://localhost:8086/ ( admin - admin123 )<br />

![Capture d’écran 2022-12-03 174553](https://user-images.githubusercontent.com/17914107/205452057-55784235-5a5f-4fe5-b5ed-258c96c24719.png)

<br />

## Chronograf http://localhost:8888/
![Chronograf Power consumption analysis](https://user-images.githubusercontent.com/17914107/205452034-a7380b78-bae1-4797-a961-a2edfffd4d70.png)


<br />

## Steps to run the project (with MongoDB) 
<br />
1- Run "docker-compose up --build" in root direcotry<br />
2- Make sure that Mongodb , mongo express and pyapp containers are running<br />
3-Mongo container may take some time for running , and then to make sure check http://localhost:27017/ (if you see this message : "It looks like you are trying to access MongoDB over HTTP on the native driver port" means it is working 
4- Open mongo express in the browser to check the databases <br />
5- Go to kafka folder and run the procedure "python3 Procedure.py" <br /> 
6- run "docker exec -it [Spark containerID]" to be inside SPARK container then run "spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 DataPreprocessingSpark.py"<br /> 
7-  Go to inside pyapp container and run the consumer "python3 ProcessedPowerConsumptionMongo.py" (if you want to send data to MongoDB without the preprocessing run "python3 PowerConsumptionMongo.py") <br /> 
8- Open Mongo express in the browser and check the results <br />

## Mongo Express http://localhost:8081 <br />

<img width="728" alt="Capture" src="https://user-images.githubusercontent.com/56035229/205452601-6269061f-3a02-41c6-9e65-5b9df93828e5.PNG">
