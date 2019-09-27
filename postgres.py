import os
from pyspark.sql import DataFrameWriter


class PostgresConnector(object):

    def __init__(self):
        self.database_name = 'postgres'
        self.hostname = os.environ['POSTGRES_HN']
        self.url_connect = "jdbc:postgresql://{hostname}:5432/{db}".format(hostname=self.hostname, db=self.database_name)
        self.properties = {"user": os.environ['POSTGRES_UN'],
                        "password": os.environ['POSTGRES_PW'],
                        "driver": "org.postgresql.Driver"
        }

    def get_writer(self, df):
        return DataFrameWriter(df)

    def write(self, df, table, mode):
        my_writer = self.get_writer(df)
        my_writer.jdbc(self.url_connect, table, mode, self.properties)
