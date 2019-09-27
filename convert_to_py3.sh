#!/bin/bash
mkdir /home/ubuntu/MSongsDB/Python3Src
for file in $(find .)
do
    echo $file
    pt2to3 $file > temp.txt
    new_file=$(echo $file | cut -d '/' -f 2)
    mv temp.txt /home/ubuntu/MSongsDB/Python3Src/$new_file
done

