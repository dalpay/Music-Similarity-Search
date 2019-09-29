import os
import sys

from msd import MSDInterface
from spotify import SpotifyInterface
from postgres import PostgresConnector
from vectors import vector_processor

from pyspark import SparkFiles
from pyspark.sql import Row
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField
from pyspark.sql.types import StructType
from pyspark.sql.types import StringType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import IntegerType
from pyspark.sql.types import ArrayType
from pyspark.sql.functions import lit
from pyspark.sql.functions import udf
from pyspark.sql.functions import monotonically_increasing_id


class MusicProcessor:

    def __init__(self, num_songs, data_source, vector_method):

        self.num_songs = num_songs
        self.data_source = data_source
        self.vector_method = vector_method

        self.spark = SparkSession.builder.appName('MusicSimilarity').getOrCreate()

        if (data_source == 'msd'):
            self.interface = MSDInterface()
        elif (data_source == 'spotify'):
            self.interface == SpotifyInterface()

    def run_batch_process(self):

        song_data_list = self.interface.get_music(num_songs=self.num_songs)
        song_data_df = self.spark.createDataFrame(Row(**song_dict) for song_dict in song_data_list)
        song_data_df = song_data_df.withColumn('id', monotonically_increasing_id())
        print(song_data_df.show(10))

        song_info_df = song_data_df.select('id', 'name', 'artist', 'year')
        song_info_df = song_info_df.withColumn('source', lit(self.data_source))
        print(song_info_df.show(10))

        comp_vec_udf = udf(vector_processor(method=self.vector_method), returnType=ArrayType(DoubleType()))
        song_vec_df = song_data_df.withColumn('vector', comp_vec_udf('timbre', 'chroma'))
        song_vec_df = song_vec_df.select('id', 'vector')
        song_vec_df = song_vec_df.withColumn('method', lit(self.vector_method))  
        print(song_vec_df.show(10))
        
        return song_data_df

    def write_to_db(self, dataframe, table_name):

        connector = PostgresConnector()
        connector.write(dataframe, table_name, mode='append')


def main():  
    
    num_songs = 10
    source = 'msd'
    method = 'gauss'
    music_processor = MusicProcessor(num_songs=num_songs, data_source=source, vector_method=method)
    music_processor.run_batch_process()

if (__name__ == '__main__'):
    
    main()
