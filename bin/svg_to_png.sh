#! /usr/bin/env bash

# Convert all files in the directory below to png, writing to the $PWD.

for file in ../*.svg
do
    filename=$(basename $file)
    pngfile=${filename/.svg/.png}
    if [ ! -f $pngfile ]
    then
        echo $filename
        convert -density 500 $file $pngfile
    else
        echo exists.. $pngfile
    fi
done
