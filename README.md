# Feature-Based Music Similarity Search
This repo implements a music similarity search based on features extracted from music signals. Given song that a user likes, which may be selected from searchable list of songs already in a dataset or uploaded by the user, the system will provide a ranked list of songs most similar to the given song. The million songs dataset (300 GB of diverse songs) is used to search a wide variety of songs from different genres from around the world, both contempoary and historical.

## Engineering Challenge
The focus of the project is to parallelize the process of extracting audio features with particular attention on most efficiently clustering the audio features by running multiple instances of k-means in parallel to find the clusters with the lowest homogeneity. The means of the clustering with the lowest homogeneity is then used as the feature vector that characterizes a song.

## Tools and Dependencies
- AWS S3 is used to host the Million Songs dataset as it is already an [Amazon Public Dataset](https://aws.amazon.com/datasets/million-song-dataset/).
- Spark is used to process the music files in parallel. 
- Librosa is used to extract audio features.

## References
1. [Million songs dataset](http://millionsongdataset.com/)
2. []()
