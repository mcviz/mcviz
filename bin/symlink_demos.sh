#! /usr/bin/env bash

# Create directories for each tool type, and symlink files into them
INDIR=$1

for TOOLTYPES in $(ls -1 $INDIR | awk -F- '{ print $(NF-1)"-"$NF }' | cut -d. -f1 | sort -u)
do
    echo Processing $TOOLTYPES
    DIR=links/${TOOLTYPES/-/\/}
    mkdir -p $DIR
    for file in $(ls -1 $INDIR | grep $TOOLTYPES)
        do ln -s $(pwd)/$INDIR/$file $DIR/
    done
done

