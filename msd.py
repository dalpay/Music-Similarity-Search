import os
import sys

h5_lib_path = '/home/ubuntu/MSongsDB/Python3Src'
sys.path.append(h5_lib_path)
import hdf5_getters as h5


class MSDInterface:

    def __init__(self):

        root_path = '/home/ubuntu/msd/data/'
        self.root_path = root_path

    def get_songs(self, all_data=True, num_songs=20):

        files_list = self.get_files(all_data=all_data, num_songs=num_songs)
        song_data = [self.process_song(file) for file in files_list]

        return song_data

    def get_files(self, all_data=False, num_songs=20):

        subset_path = 'A/A/A/'
        data_path = self.root_path if all_data else os.path.join(self.root_path, subset_path)

        files_list = []
        for root, dirs, files in os.walk(data_path):

            files_subset = [os.path.join(root, f) for f in files if f.endswith('.h5')]
            files_list += files_subset

        return files_list[:num_songs]

    def process_song(self, song_path):

        song_data = h5.open_h5_file_read(song_path)
        
        song_id = h5.get_song_id(song_data).decode('UTF-8')
        song_name = h5.get_title(song_data).decode('UTF-8')
        artist_name = h5.get_artist_name(song_data).decode('UTF-8')
        song_year = int(h5.get_year(song_data))
        
        timbre = h5.get_segments_timbre(song_data)
        chroma = h5.get_segments_pitches(song_data)
        
        song_data.close()
        song_dict = {'id': song_id, 'name': song_name, 'artist': artist_name, 
                    'year': song_year, 'timbre': timbre, 'chroma': chroma}
        return song_dict


def main():

    msdi = MSDInterface()
    songs = msdi.get_songs(all_data=False, num_songs=3)
    print(songs)
    print(len(songs))
    print(songs[0].keys())

if (__name__ == '__main__'):
    
    main()
