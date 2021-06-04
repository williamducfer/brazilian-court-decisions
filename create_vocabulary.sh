#!/bin/bash

if [ $# -ne 3 ]; then
	echo "Usage: $0 directory_with_files number_of_columns output_filename_prefix"
	exit 1
fi

DIR_WITH_FILES=$1
NUM_COLUMNS=$2
OUTPUT_FILENAME_PREFIX=$3

for COL in `seq $NUM_COLUMNS`; do
	OUTPUT_FILENAME=${OUTPUT_FILENAME_PREFIX}${COL}
	echo "Creating a vocabulary for column \"${COL}\" and saving to file \"${OUTPUT_FILENAME}\"..."
	cut -f${COL} ${DIR_WITH_FILES}/* | sort | uniq > ${OUTPUT_FILENAME}
done
