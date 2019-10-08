#!/bin/bash
block_size=500
for ind in {0..2000}
do
    block_offset=$(($block_size * $ind))
    echo $block_offset
    nohup spark-submit --master local[*] /home/ubuntu/project/processing/spark_processing.py --number "$block_size" --offset "$block_offset" --source "msd" --method "gauss"
done
