# Airline-Delay-Data
Airline On-Time Statistics and Delay Causes Data (2003-2022)

# Overview
Starting in 2003, the Bureau of Transportation Statistics (BTS) began recording the causes of flight delays as reported by various airline carriers. The goal of this project is to create a data pipeline to download this flight delay data, save it to a Data Warehouse and finally perform analysis to visualize the data using Google Data Studio. 

# Dataset Description

A full description from the BTS about the dataset can be found [here](https://www.bts.dot.gov/explore-topics-and-geography/topics/airline-time-performance-and-causes-flight-delays).  A flight is counted as "on time" if it operated less than 15 minutes later than the scheduled time shown in the carriers' Computerized Reservations Systems (CRS). Arrival is based on arrival at the gate and departure is based on departure from the gate. As per the BTS, the reporting airlines are:
- Alaska Airlines
- Allegiant Air
- American Airlines
- Delta Air Lines
- Endeavor Air
- Envoy Air
- Frontier Airlines
- Hawaiian Airlines
- Horizon Air
- JetBlue Airways
- Mesa Airlines
- PSA Airlines
- Republic Airlines
- SkyWest Airlines
- Southwest Airlines
- Spirit Airlines
- United Airlines

# Data Format
The .csv file contains the following columns
- year = year of flight
- month = month of flight
- carrier = 2 character airline carrier code
- carrier_name = name of the airline carrier
- airport = 3 character airport code
- airport_name = city, state: name of the airport
- arr_flights = number of arriving flights
- arr_del15 =  number of flights delayed (>= 15minutes late)
- carrier_ct = number of flights delayed due to air carrier (e.g. maintenance or crew problems, aircraft cleaning, fueling etc.)
* weather_ct = number of flights delayed due to weather
* nas_ct = number of flights delayed due to National Aviation System (e.g. non-extreme weather conditions, heavy traffic volume, air traffic control, etc.)
* security_ct = number of flights delayed due to security (e.g. re-boarding of aircraft because of security breach, inoperative screening equipment and/or long lines in excess of 29 minutes at screening areas)
* late_aircraft_ct = number of flights delayed due to a previous flight using the same aircraft being late.
* arr_cancelled = number of cancelled flights
* arr_diverted = number of diverted flights
* arr_delay = total time (minutes) of delayed flights
* carrier_delay = total time (minutes) of delayed flights due to air carrier
* weather_delay = total time (minutes) of delayed flights due to weather
* nas_delay = total time (minutes) of delayed flights due to National Aviation System
* security_delay = total time (minutes) of delayed flights due to security issues
* late_aircraft_delay = total time (minutes) of delayed flights due to a previous flight using the same aircraft being late.

# Architecture Proposal

![alt workflow](https://github.com/Raatid-Dilly/Airline-Delay-Data/blob/main/images/airline_workflow.jpg)

**Infrastructure**:
  * Terraform - Terraform is used to setup the inital data lake and data warehouse that will be used for storage
  * Google Cloud Platform - Google Cloud Platform hosts the cloud storage of the data lake and data warehouse
  * Docker - A docker container is used to run Apache Airflow to get the data
  
**Workflow Orchestration**
  * Apache Airflow - Airflow is used to orchestrate the data ingestion from the BTS source and upload the data to GCS data lake and GCS BigQuery
  
**Data Transformation**
  * Dbt Cloud - Dbt (data build tool) is used for the performing the final data transformations for the pipeline and for sending the data to the production database
  
**Data Visualization**
  * Google Data Studio - Used to visualize the data


# Work
### GCP Setup:

To begin, you will need a Google Cloud Platform account or any cloud provide like AWS or Azure. This demonstration will focus on GCP.
After creating a GCP account, create a new project with an unique Project ID (this Project ID will be reference by Terraform to create the data lake and data warehouse). Next you will need to setup service account and authentication for the project. Help on doing this can be found [here](https://cloud.google.com/docs/authentication/client-libraries). The following roles should be granted to the project:

  - Storage Admin
  - Storage Object Admin
  - BigQuery Admin
  - Viewer
 
After granting the roles listed above to the account, download the service-account-keys .json file that will be needed for authentication. Additionally, download the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk) to develop locally through a CLI. Set an environment variable to point to the downloaded GCP .json authentication key like such:

``` 
export GOOGLE_APPLICATION_CREDENTIALS="<path-to-your-service-account-authkeys>.json"
#Then enter
gcloud auth application-default login
```

### Terraform:

After the GCP account is setup and the authentication keys are downloaded, next is Terraform. Terraform is an open-source tool by HashiCorp used for provisioning infrastructure resources. The [IaC(Terraform)](https://github.com/Raatid-Dilly/Airline-Delay-Data/tree/main/IaC(Terraform)) folder contains the ```main.tf``` and ```variables.tf``` files which are essentially the configuration files for creating the resources.  [This](https://learn.hashicorp.com/collections/terraform/gcp-get-started) is a great resource for learning about using Terraform with Google Cloud. To execute Terraform commands, cd into the folder with a CLI and perform:

- ```terraform init``` - To initialize the configuration
- ```terraform plan``` - Matches/previews local changes against a remote state and proposes an execution plan (May need to specify GCP Project ID)
- ```terraform apply``` - Applies the changes to the cloud (May need to specify GCP Project ID)
- ```terraform destroy``` - Removes stack from the cloud

### Apache Airflow:

Now that the cloud resources were created by Terraform next is orchestrating the workflow with Airflow. First create an airflow folder and inside create folders called ```dags```, ```logs```, and ```plugins```. To run Airflow locally we will use Docker which require both a [Dockerfile](https://github.com/Raatid-Dilly/Airline-Delay-Data/blob/main/airflow/Dockerfile) and a [docker-compose.yaml](https://github.com/Raatid-Dilly/Airline-Delay-Data/blob/main/airflow/docker-compose.yaml) file. Both of these files should be in your airflow folder as well. The docker-compose.yaml file is the official airflow docker file but with additional variable for our needs such as the following:

```
 GOOGLE_APPLICATION_CREDENTIALS: <PATH TO YOUR GOOGLE APPLICATIONS CREDENTIALS .json FILE>
 AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT: 'google-cloud-platform://?extra__google_cloud_platform__key_path=<PATH TO YOUR GOOGLE APPLICATIONS CREDENTIALS .json FILE>'
 GCP_PROJECT_ID: '<YOUR GCP PROJECT NAME/ID>' 
 GCP_GCS_BUCKET: '<YOUR GCP GOOGLE CLOUD STORAGE DATA LAKE BUCKET NAME>'
 volumes:
   - ./dags:/opt/airflow/dags
   - ./logs:/opt/airflow/logs
   - ./plugins:/opt/airflow/plugins
```

To run Airflow ```cd <path-to-your-airflow-folder>``` and run the following shell commands:
  - ```docker-compose build``` - Builds the docker image
  - ```docker-compose up airflow-init``` - Initializes all the Airflow components
  - ```docker-compose up -d``` - Starts all the services in the container and runs in detached mode so you can still use the terminal
  
To view the Airflow UI open a web browser and go to ```https://localhost:8080``` and enter ```airflow``` for both the username and password. The DAG that is listed in the [airflow/dags](https://github.com/Raatid-Dilly/Airline-Delay-Data/tree/main/airflow/dags) folder should be listed on the UI page. Simply run the DAG and wait for it to be finish. When complete the tasks that are described in the DAG should have all been executed and the airline delay data should now be in your GCS data lake and as an External Table in Google BigQuery. To stop Airflow, run the following in your terminal:

  - ```docker-compose down```
  
### dbt Cloud:

dbt Cloud will be used for the final data transformation and for writing the data to the production data warehouse.  A [dbt account](https://www.getdbt.com/signup/) is required and it will need to be connected to Google BigQuery. Follow this [tutorial](https://docs.getdbt.com/guides/getting-started/getting-set-up/setting-up-bigquery) to setup a connection between the two. The ```dbt/macros``` and ```dbt/models``` folders contain the code used to execute the transformations and all ```dbt``` files are [here](https://github.com/Raatid-Dilly/Airline-Delay-Data/tree/main/dbt).

### Google Data Studio

After using dbt Cloud to write the data to your production dataset, it is time to visualize the data. The final dashboard contains 2 pages and can contains several dropdown fields on each page such as ```State``` and ```Carrier```.  From the data it is clear that California and Florida have the most delayed flights and that during the pandemic of 2020 there was an estimated 2 million fewer flights compared to 2019.  It should be noted that although the amount of minutes of flights delay cause by weather is significantly lower than that of the other fields, this is not the true value for this field. As [per the BTS](https://www.bts.gov/topics/airlines-and-airports/understanding-reporting-causes-flight-delays-and-cancellations) the field of weather delays consists of extreme weather that prevents flying. There is another category of weather within the NAS category. This type of weather slows the operations of the system but does not prevent flying. 

![alt dashboard](https://github.com/Raatid-Dilly/Airline-Delay-Data/blob/main/images/Airline_On-Time_Statistics_and_Delays%20(1).jpg)
