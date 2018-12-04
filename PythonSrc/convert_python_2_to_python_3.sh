#!/bin/bash
for f in $(find .)
do
    echo $f
    pt2to3 $f > temp.txt
    mv temp.txt $f
done
