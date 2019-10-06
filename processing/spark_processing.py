#!/usr/bin/env python3
import os
import sys
import argparse
import faiss
import numpy as np

from msd import MSDInterface
from spotify import SpotifyInterface
from postgres import PostgresConnector
from vectors import vector_processor

from pyspark import SparkFiles
from pyspark.sql import Row
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import ArrayType
from pyspark.sql.functions import lit
from pyspark.sql.functions import udf
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.functions import row_number


class MusicProcessor:
    '''
    Retrieves a number of songs from either the Million Song Dataset or the 
    Spotify API, distributes the processing of each song across Spark workers
    to extract the embedding vector of each song, and writes the song 
    information and embedding vectors to a Postgres DB. 
    '''

    def __init__(self, num_songs, songs_offset, data_source, vector_method):

        self.num_songs = num_songs
        self.songs_offset = songs_offset
        self.data_source = data_source
        self.vector_method = vector_method

        self.spark = SparkSession.builder.appName('MusicSimilarity').getOrCreate()
        self.spark.sparkContext.addPyFile('vectors.py')

        self.spark.conf.set('spark.dynamicAllocation.enable', 'true')
        self.spark.conf.set('spark.dynamicAllocation.executorIdleTimeout', '2m')
        self.spark.conf.set('spark.dynamicAllocation.minExecutors', '1')
        self.spark.conf.set('spark.dynamicAllocation.maxExecutors', '2000')
        self.spark.conf.set('spark.stage.maxConsecutiveAttempts', '10')
        self.spark.conf.set('spark.memory.offHeap.enable', 'true')
        self.spark.conf.set('spark.memory.offheap.size', '3g')
        self.spark.conf.set('spark.executor.memory', '5g')
        self.spark.conf.set('spark.driver.memory', '5g')

        self.db_writer = PostgresConnector()

        if (data_source == 'msd'):
            self.interface = MSDInterface()
        elif (data_source == 'spotify'):
            self.interface = SpotifyInterface()

    def run_batch_process(self):
        
        # Retrieve songs from interface and construct DF
        song_data_list = self.interface.get_music(num_songs=self.num_songs, offset=self.songs_offset)
        song_data_df = self.spark.createDataFrame(Row(**song_dict) for song_dict in song_data_list)
        
        # Build song information DF
        song_info_df = song_data_df.select('id', 'source_id', 'name', 'artist', 'year')
        song_info_df = song_info_df.withColumn('source', lit(self.data_source))

        # Build song vector DF
        comp_vec_udf = udf(vector_processor(method=self.vector_method), returnType=ArrayType(DoubleType()))
        song_vec_df = song_data_df.withColumn('vector', comp_vec_udf('timbre', 'chroma'))
        song_vec_df = song_vec_df.select('id', 'vector')
        song_vec_df = song_vec_df.withColumn('method', lit(self.vector_method))

        # Write vectors to the similarity search index
        self.write_to_faiss(song_vec_df)

        # Write DFs to DB
        self.db_writer.write(song_info_df, 'song_info', mode='append')
        self.db_writer.write(song_vec_df, 'song_vectors', mode='append')

    def write_to_faiss(self, vec_df):

        index_filename = self.data_source + '_' + self.vector_method + '.index'
        
        if (os.path.isfile(index_filename)):
            index = faiss.read_index(index_filename)
        else:
            sample_vec = vec_df.limit(1).collect()[0].vector
            num_dimensions = len(sample_vec)
            index_key = 'IDMap,ITQ,LSH'
            index = faiss.index_factory(num_dimensions, index_key)
        
        vec_table = vec_df.select('id', 'vector').collect()
        ids_list = [row.id for row in vec_table]
        vecs_list = [row.vector for row in vec_table]
        ids_arr = np.array(ids_list, copy=False, dtype=np.int64)
        vecs_arr = np.array(vecs_list, copy=False, dtype=np.float32)

        index.train(vecs_arr)
        index.add_with_ids(vecs_arr, ids_arr)
        faiss.write_index(index, index_filename)

def get_parser():

    parser = argparse.ArgumentParser(
        description='Processes songs retrieved from either MSD or Spotify'
    )
    parser.add_argument('-n', '--number', 
        help='Specify the number of songs to retrieve from the data source', 
        required=True, type=int
    )
    parser.add_argument('-o', '--offset',
        help='Specify the offset from the beginning of the list of songs',
        default=0, type=int)
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
                                songs_offset=args.offset,
                                data_source=args.source, 
                                vector_method=args.method)
    music_processor.run_batch_process()

if (__name__ == '__main__'):
    
    main()
