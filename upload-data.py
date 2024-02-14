# import dependices
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from time import time, sleep
import socket

# check postgreSQL service is ready to accept conection
def is_postgres_ready(host, port, timeout=10):
    while timeout > 0:
        try:
            with socket.create_connection((host, port), timeout=1):
                print("PostgreSQL is ready to accept connections")
                return True
        # postgres service is not ready it will wait and try again
        except OSError:
            print("PostgreSQL is not yet ready, waiting...")
            sleep(1)
            timeout -= 1
    # connection faild 
    print("Timed out waiting for PostgreSQL to become ready")
    return False


if __name__ == "__main__":
    # set the host and port for connection
    postgres_host = "pgdatabase"
    postgres_port = 5432
    while not is_postgres_ready(postgres_host, postgres_port):
        print("PostgreSQL is not ready yet. Retrying in 30 second...")
        sleep(30)

    print("PostgreSQL is ready. Proceeding with the script...")

    df = pd.read_csv('yellow_tripdata_2021-01.csv', nrows=100)

    # create engine and connect to the postgreSQL service
    engine = create_engine('postgresql://root:root@pgdatabase:5432/ny_taxi')

    # check table schema
    print(pd.io.sql.get_schema(df, 'yellow_taxi_data', con=engine))
    
    # change columns to datetime in pandas
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # create the table and put the columns header
    df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')

    # upload the data to the database in chunks
    df_iter = pd.read_csv('yellow_tripdata_2021-01.csv', iterator=True, chunksize=100000)

    while True:
        t_start = time()

        try:
            df = next(df_iter)
        except StopIteration:
            print('No more data to upload.')
            break

        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')

        t_end = time()

        print('Inserted another chunk, took %.3f seconds' % (t_end - t_start))

    # upload the zone file into a new table
    print('Upload the zone table')
    df_zones = pd.read_csv('taxi_zone_lookup.csv')
    df_zones.to_sql(name='zones', con=engine, if_exists='replace')
    print('Done')