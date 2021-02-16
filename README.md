# Project 1: Data Modelling with Postgres

# Project use case
A startup called Sparkify wants to analyse the data they have been collecting on song and user activity on their new streaming app. 

The analytics team is particularly interested in understanding what songs users are listening to. Currently they cannot do this easily as their data on user activity and song attributes are stored in JSON files.

# Project requirements

- To create a Postgres database with tables designed to optimize queries on song play analysis.

- To define fact and dimension tables for a star schema for a particular analytic focus, and write an ETL pipeline that transfers data from files in two local directories into these tables in Postgres using Python and SQL.

- To test the database and ETL pipeline by running queries given by the analytics team from Sparkify and compare your results with their expected results.

# Raw files

1. Song Dataset  

   Each song file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID e.g.song_data/A/B/C/TRABCEI128F424C983.json  
   
   {"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}

2. Log Dataset  

   Each log data file is in JSON format and contains information about user activity whilst using the platform e.g. song plays.  
   
   The log files in the dataset you'll be working with are partitioned by year and month e.g. log_data/2018/11/2018-11-12-events.json  
   
   {"artist":"Pavement", "auth":"Logged In", "firstName":"Sylvie", "gender", "F", "itemInSession":0, "lastName":"Cruz", "length":99.16036, "level":"free", "location":"Klamath Falls, OR", "method":"PUT", "page":"NextSong", "registration":"1.541078e+12", "sessionId":345, "song":"Mercy:The Laundromat", "status":200, "ts":1541990258796, "userAgent":"Mozilla/5.0(Macintosh; Intel Mac OS X 10_9_4...)", "userId":10}

# Data model

A star schema has been implemented to structure this data and enable optimised queries on song play analysis as per the business requirements. Details below.

## Fact Table

**Table songplays**

| COLUMN  	| TYPE  	| CONSTRAINT  	|
|---	|---	|---	|	
|   songplay_id	| SERIAL  	|   PRIMARY KEY NOT NULL    | 
|   start_time	|   timestamp	|   	| 
|   user_id	|   int	|   NOT NULL	| 
|   level	|   text |   	| 
|   song_id	|   text	|   	| 
|   artist_id	|   text	|   	| 
|   session_id	|   int	|   	| 
|   location	|   text	|   	| 
|   user_agent	|   text	|   	| 

The songplay_id field is the primary key and it is an auto-incremental value.

## Dimension Tables

**Table users**
 
 | COLUMN  	| TYPE  	| CONSTRAINT  	|
|---	|---	|---	|	
|   user_id	| int  	|   PRIMARY KEY	| 
|   first_name	|   text	| NOT NULL 	| 
|   last_name	|   text	|  NOT NULL	| 
|   gender	|   text |   	| 
|   level	|   text	|   	| 


**Table songs**

 | COLUMN  	| TYPE  	| CONSTRAINT   	|
|---	|---	|---	|	
|   song_id	| varchar  	|   PRIMARY KEY	| 
|   title	|   text	| NOT NULL 	| 
|   artist_id	|   text	|   	| 
|   year	|   int |   	| 
|   duration	|   float	|   NOT NULL	| 

**Table artists**

 | COLUMN  	| TYPE  	| CONSTRAINT   	|
|---	|---	|---	|	
|   artist_id	| text  	|   PRIMARY KEY	| 
|   name	|   text	|  NOT NULL 	| 
|   location	|   text	|   	| 
|   latitude	|   float	|   	| 
|   longitude	|   float |   	| 

**Table time**
 
 | COLUMN  	| TYPE  	| CONSTRAINT   	|
|---	|---	|---	|	
|   start_time	| times  	|   PRIMARY KEY	| 
|   hour	|   int	|   	| 
|   day	|   int	|   	| 
|   week	|   int	|   	| 
|   month	|   int	|   	| 
|   year	|   int	|   	| 
|   weekday	|   int	|   	| 

# Extract Transform and Load Pipeline 
The ETL process is defined in the etl.py file and is the logic is as follows:  

1. Connect to Postgres Database
2. Process song files:
		1. Fetch all paths of the files in the **song_data** directory.
		2. Insert song data into **songs** dimension.
		3. Insert artist data into **artists** dimension.
3. Process log files:
		1. Fetch all paths of the files in the **log_data** directory.
		2. Filter log data for records associated with song plays i.e. records where "field" equals NextSong
		3. Insert time metrics (e.g. year, month, day etc.) into **time** dimension -> extracted from the "ts" field
4. Insert user data into **users** dimension.
5. Insert songplay records into **songplays** fact.
		1. First, query the **songs** and **artist** dimensions to get the song_id and artist_id for the songplays records.
		2. Insert rows. 
				
# Files in repository

```
.
├── create_tables.py       Script to create database and tables
├── data/                  Folder that contains the raw data (e.g. logs)
├── etl.ipynb              Notebook that explains ETL process for subset of data.
├── etl.py                 Script to load data from raw files into the database tables
├── README.md              Documentation
├── sql_queries.py         SQL queries called in the etl.py script
└── test.ipynb             Notebook that test database table content following ETL process.
```

# Running project
1. Clone repository
2. For local development install Postgres DB and configure
3. Before running the ETL process; create the tables in the Postgres DB    
```
python create_tables.py
```
4. Run ETL script to populate the DB
```
python etl.py
```