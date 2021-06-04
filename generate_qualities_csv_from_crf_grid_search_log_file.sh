#!/bin/bash

if [ $# -ne 2 ]; then
	echo "Usage: $0 qualities_log_file_path output_file_path"
	exit 1
fi

QUALITIES_FILE_PATH=$1
OUTPUT_FILE_PATH=$2
FILE_TYPE=$3

echo "Model,Precision,Recall,F1" >> $OUTPUT_FILE_PATH

sed -n "/^\(For \|Mean quality of cross-validation\)/p" $QUALITIES_FILE_PATH |
sed -z "s/For \([^a]*\)and \([^\n]*\)\nMean quality of cross-validation: precision = \([^ ]*\), recall = \([^ ]*\), f1 = \([^ \n]*\)/Parameters: \1; \2,\3,\4,\5/g" >> $OUTPUT_FILE_PATH
