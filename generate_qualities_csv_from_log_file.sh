#!/bin/bash

if [ $# -ne 3 ]; then
	echo "Usage: $0 qualities_log_file_path output_file_path [grid_search|evaluation]"
	exit 1
fi

QUALITIES_FILE_PATH=$1
OUTPUT_FILE_PATH=$2
FILE_TYPE=$3

echo "Model,Precision,Recall,F1" >> $OUTPUT_FILE_PATH

if [ $FILE_TYPE == "evaluation" ]; then
    sed -n "/^\(Model file\|precision\|recall\|f1\)/p" $QUALITIES_FILE_PATH |
    sed -z "s/Model file: \"\([^\"]*\)\"/\1/g" |
    sed -z "s/\n\(precision\|recall\|f1\): \([^ ]*\) percent/,\2/g" >> $OUTPUT_FILE_PATH
elif [ $FILE_TYPE == "grid_search" ]; then
    sed -n "/^\(Model ([^)]*) architecture\|Mean quality of cross-validation\)/p" $QUALITIES_FILE_PATH |
    sed -z "s/Model (\([^)]*\)) architecture[^\n]*\nMean quality of cross-validation: precision = \([^ ]*\), recall = \([^ ]*\), f1 = \([^ \n]*\)/Model \1,\2,\3,\4/g" |
    sed "/^\(Model ([^)]*) architecture\|Mean quality of cross-validation\)/d" >> $OUTPUT_FILE_PATH
else
    echo "Error: expected \"grid_search\" or \"evaluation\" as file type."
fi
