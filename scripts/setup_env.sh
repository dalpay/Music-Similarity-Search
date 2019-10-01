#!/bin/bash

cd /home/ubuntu/Downloads
 
wget "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
chmod u+x Miniconda3-latest-Linux-x86_64.sh
/bin/bash Miniconda3-latest-Linux-x86_64.sh -b
source ~/miniconda3/bin/activate

cd ~
conda create --name py35 python=3.5 --file spec_file.txt
echo "Inserted by script"
echo "source ~/miniconda3/bin/activate" >> "/home/ubuntu/.bashrc"
echo "conda activate py35" >> "/home/ubuntu/.bashrc"
source ~/.bashrc
conda activate py35

cd ~
git clone "https://github.com/plamere/spotipy.git" "/home/ubuntu/spotipy"
cd "/home/ubuntu/spotipy"
python setup.py install

