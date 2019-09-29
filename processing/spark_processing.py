import os
import sys
import argparse

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
    '''
    Retrieves a number of songs from either the Million Song Dataset or the 
    Spotify API, distributes the processing of each song across Spark workers
    to extract the embedding vector of each song, and writes the song 
    information and embedding vectors to a Postgres DB. 
    '''

    def __init__(self, num_songs, data_source, vector_method):

        self.num_songs = num_songs
        self.data_source = data_source
        self.vector_method = vector_method

        self.spark = SparkSession.builder.appName('MusicSimilarity').getOrCreate()
        self.db_writer = PostgresConnector()

        if (data_source == 'msd'):
            self.interface = MSDInterface()
        elif (data_source == 'spotify'):
            self.interface = SpotifyInterface()

    def run_batch_process(self):
        '''
        
        '''

        # Retrieve songs from interface and construct DF
        song_data_list = self.interface.get_music(num_songs=self.num_songs)
        song_data_df = self.spark.createDataFrame(Row(**song_dict) for song_dict in song_data_list)
        song_data_df = song_data_df.withColumn('id', monotonically_increasing_id())
        print(song_data_df.show(10))

        # Build song information DF
        song_info_df = song_data_df.select('id', 'name', 'artist', 'year')
        song_info_df = song_info_df.withColumn('source', lit(self.data_source))
        print(song_info_df.show(10))

        # Build song vector DF
        comp_vec_udf = udf(vector_processor(method=self.vector_method), returnType=ArrayType(DoubleType()))
        song_vec_df = song_data_df.withColumn('vector', comp_vec_udf('timbre', 'chroma'))
        song_vec_df = song_vec_df.select('id', 'vector')
        song_vec_df = song_vec_df.withColumn('method', lit(self.vector_method))  
        print(song_vec_df.show(10))
        
        # Write DFs to DB
        # self.db_writer.write(song_info_df, 'table_name', mode='append')
        # self.db_writer.write(song_info_df, 'table_name', mode='append')

def get_parser():

    parser = argparse.ArgumentParser(
        description='Processes songs retrieved from either MSD or Spotify'
    )
    parser.add_argument('-n', '--number', 
        help='Specify the number of songs to retrieve from the data source', 
        required=True, type=int
    )
    parser.add_argument('-s', '--source',  
        help='Select either "msd" or "spotify" as the data source', 
        choices=['msd', 'spotify'],
        required=True, type=str
    )
    parser.add_argument('-m', '--method', 
        help='Select the method to process the songs with',
        choices=['gauss', 'gmm', 'pca'], 
        default='gauss', type=str
    )

    return parser

def main():  
    
    parser = get_parser()
    args = parser.parse_args()
    music_processor = MusicProcessor(num_songs=args.number, 
                                data_source=args.source, 
                                vector_method=args.method)
    music_processor.run_batch_process()

if (__name__ == '__main__'):
    
    main()
