# Project: Data Pipelines with Apache Airflow

## Contents

+ [Overview](#Overview)
+ [Project Data](#Project-Data)
+ [Workflow](#Workflow)

## Overview

A music streaming company, Sparkify, has decided that it is time to introduce more automation and monitoring to their data warehouse ETL pipelines and come to the conclusion that the best tool to achieve this is Apache Airflow.

They have decided to bring you into the project and expect you to create high grade data pipelines that are dynamic and built from reusable tasks, can be monitored, and allow easy backfills. They have also noted that the data quality plays a big part when analyses are executed on top the data warehouse and want to run tests against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.

The source data resides in S3 and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.

## Project Data

For this project, there are two datasets.

>**s3://udacity-dend/song_data/**<br>
>**s3://udacity-dend/log_data/**

## Workflow

### Data Modeling

Using the song and event datasets, we'll create a star schema optimized for queries on song play analysis:
- Fact Table
    - songplays: records in event data associated with song plays i.e. records with page NextSong
- Dimension Tables
    - users: users in the app
    - songs: songs in music database
    - artists: artists in music database
    - time: timestamps of records in songplays broken down into specific units

We also need to create AWS Redshift cluster and IAM Role for the project.

### Create tables in Redshift database

You can use **Query Editor** in AWS Console to create tables. Queries to create tables are stored in **create_tables.py**

### DAG Configuration

Default parameter for DAG:

1. The DAG does not have dependencies on past runs
2. On failure, the task are retried 3 times. Retries happen every 5 minutes
3. Catchup is turned off
4. Do not email on retry
5. DAG will be run hourly

The final graph view follows the flow shown in the image below.

![Example-DAG](readme_image/result.PNG)

### Building the operators

#### Stage Operator

The stage operator is expected to be able to load any JSON formatted files from S3 to Amazon Redshift. The operator creates and runs a SQL COPY statement based on the parameters provided. The operator's parameters should specify where in S3 the file is loaded and what is the target table.

The parameters should be used to distinguish between JSON file. Another important requirement of the stage operator is containing a templated field that allows it to load timestamped files from S3 based on the execution time and run backfills.

#### Fact and Dimension Operators

With dimension and fact operators, you can utilize the provided SQL helper class to run data transformations. Most of the logic is within the SQL transformations and the operator is expected to take as input a SQL statement and target database on which to run the query against. You can also define a target table that will contain the results of the transformation.

Dimension loads are often done with the truncate-insert pattern where the target table is emptied before the load. Thus, you could also have a parameter that allows switching between insert modes when loading dimensions. Fact tables are usually so massive that they should only allow append type functionality.

#### Data Quality Operator

The final operator to create is the data quality operator, which is used to run checks on the data itself. The operator's main functionality is to receive one or more SQL based test cases along with the expected results and execute the tests. For each the test, the test result and expected result needs to be checked and if there is no match, the operator should raise an exception and the task should retry and fail eventually.

Example log for quality is shown as below:

![Example-quality-check](readme_image/data_quality.PNG)
