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

