# Real-time-power-consumption-analysis-
With the electricity consumption being so crucial worldwide, the idea is to study the impact on energy consumption. The dataset is exhaustive in its demonstration of energy consumption of the Tétouan city in Morocco. The distribution network is powered by 3 Zone stations.The data consists of 52,416 observations of energy consumption on a 10-minute window. Every observation is described by 9 feature columns.

Project architecture diagram

![architecture](https://user-images.githubusercontent.com/17914107/201059480-6cc7c7a5-e341-4e85-84c0-1d6253925cad.png)


Steps to run the project :
1- Run "docker-compose up" in root direcotry
2- Generate new Influxdb credentials (api token) and replace it in .env , telegraf/teleraf.conf and loadStream.py
3- Run "docker-compose down" then "docker-compose up" 
2- Go to kafka folder and run "python3 processStream.py" then "python3 loadStream.py"
3- Create a new Influxdb data source in Grafana 

Influxdb http://localhost:8086/ ( admin - admin123 )

![influxdb](https://user-images.githubusercontent.com/17914107/201059618-1e2e6d4a-64f0-4d60-aaee-8c9577018873.png)

Grafana http://localhost:3000/ ( admin - admin )

![Grafana](https://user-images.githubusercontent.com/17914107/201059564-3c2dacc0-044f-48f4-b645-eddd398ae387.png)

