import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """
    Description: This function takes a json file from the song_data directory,
    transforms the data and loads into several tables in the postgres database:
    Songs (dimension), Artists (Dimension).
    
    Args:
        cur: the cursor object.
        filepath: filepath of json file withing log_data directory
    
    Returns:
        None
    """
    # open song file
    df = pd.read_json(filepath , typ='series')

    # insert song record
    song_data = df[["song_id", "title", "artist_id", "year", "duration"]]
    song_data = list(song_data.values)
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_data = df[['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']]
    artist_data = list(artist_data.values)
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    Description: This function takes a json file from the log_data directory,
    transforms the data and loads into several tables in the postgres database:
    Time (dimension), Users (Dimension) and Songplays (Fact).    
    
    Args:
        cur: the cursor object.
        filepath: filepath of json file withing log_data directory
    
    Returns:
        None
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page'] == 'NextSong']

    # convert timestamp column to datetime
    df["ts"] = pd.to_datetime(df["ts"], unit='ms')
    
    # insert time data records
    #  timestamp, hour, day, week of year, month, year, and weekday
    time_df = pd.DataFrame({
        "start_time": df["ts"].dt.time,
        "hour": df["ts"].dt.hour,
        "day": df["ts"].dt.day,
        "week": df["ts"].dt.week,
        "month": df["ts"].dt.month,
        "year": df["ts"].dt.year,
        "weekday": df["ts"].dt.weekday
    })

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (row.ts, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    This function is responsible for fetching all filepaths (json) within the supplied directory
    and for each file: executes the ingestion pipeline (dependent on the supplied function) that
    extracts, transforms and loads the data into the database.
    
    Args:
        cur: the cursor object.
        conn: connection to database.
        filepath: filepath of directory containing json files for ETL process.
        func: function that does the ETL process into the database.
    
    Returns:
        None
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """
    This function:
        - Connects to Postgres Database and create cursor object 
        - Executes process_data function for song_data files
        - Executes process_data function for log_data files
        - Close connection to Postgres DB
        
    Returns:
        None
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()