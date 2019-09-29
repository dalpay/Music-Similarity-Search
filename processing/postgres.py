import os
from pyspark.sql import DataFrameWriter


class PostgresConnector(object):
    '''
    Interface between Spark and Postgres DB to write PySpark dataframes to 
    Postgres DB tables.
    '''

    def __init__(self):

        self.database_name = 'postgres'
        self.hostname = os.environ['POSTGRES_HN']
        self.url_connect = "jdbc:postgresql://{hostname}:5432/{db}".format(hostname=self.hostname, db=self.database_name)
        self.properties = {
                        "user": os.environ['POSTGRES_UN'],
                        "password": os.environ['POSTGRES_PW'],
                        "driver": "org.postgresql.Driver"
        }

    def write(self, df, table, mode='append'):

        writer = DataFrameWriter(df)
        writer.jdbc(self.url_connect, table, mode, self.properties)
