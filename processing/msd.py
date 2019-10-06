import os
import sys

h5_lib_path = '/home/ubuntu/MSongsDB/Python3Src'
sys.path.append(h5_lib_path)
import hdf5_getters as h5


class MSDInterface:
    '''
    Retrieves song data from the Million Song Dataset.
    '''
    
    def get_music(self, num_songs=50, offset=0, all_songs=False):

        files_list = self.get_files(all_data=True)
        if (not all_songs and len(files_list) > num_songs):
            files_list = files_list[offset : offset + num_songs]
        songs = [self.process_song(file) for file in files_list]

        return songs

    def get_files(self, all_data=False):
        
        root_path = '/home/ubuntu/msd/data/'
        subset_path = 'A/'

        data_path = root_path if all_data else os.path.join(root_path, subset_path)

        files_list = []
        for root, dirs, files in os.walk(data_path):

            files_subset = [os.path.join(root, f) for f in files if f.endswith('.h5')]
            files_list += files_subset

        return files_list

    def process_song(self, song_path):

        song_data = h5.open_h5_file_read(song_path)
        
        song_id = h5.get_song_id(song_data).decode('UTF-8')
        song_int_id = int(h5.get_track_7digitalid(song_data))
        song_name = h5.get_title(song_data).decode('UTF-8')
        artist_name = h5.get_artist_name(song_data).decode('UTF-8')
        song_year = int(h5.get_year(song_data))
        
        timbre = self.ndarray_list_to_ndlist(h5.get_segments_timbre(song_data))
        chroma = self.ndarray_list_to_ndlist(h5.get_segments_pitches(song_data))
        
        song_data.close()
        song_dict = {'id': song_int_id, 'source_id': song_id, 'name': song_name, 
                    'artist': artist_name, 'year': song_year, 
                    'timbre': timbre, 'chroma': chroma}
        return song_dict

    def ndarray_list_to_ndlist(self, ndarry_list):

        ndlist = [ndarr.tolist() for ndarr in ndarry_list]
        
        return ndlist

def main():

    msdi = MSDInterface()
    songs = msdi.get_music(all_data=False, num_songs=3)
    print(len(songs))
    print(songs[0].keys())

if (__name__ == '__main__'):
    
    main()
