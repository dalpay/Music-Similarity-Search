from pyspark.sql import DataFrameWriter
import os


class PostgresConnector(object):

    def __init__(self):
        self.database_name = 'postgres-db'
        self.hostname = os.environ['HOSTNAME']
        self.url_connect = "jdbc:postgresql://{hostname}:5432/{db}".format(hostname=self.hostname, db=self.database_name)
        self.properties = {"user": os.environ['USERNAME'],
                        "password": os.environ['PASSWORD'],
                        "driver": "org.postgresql.Driver"
        }

    def get_writer(self, df):
        return DataFrameWriter(df)

    def write(self, df, table, mode):
        my_writer = self.get_writer(df)
        my_writer.jdbc(self.url_connect, table, mode, self.properties)
