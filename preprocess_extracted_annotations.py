#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import csv
import numpy as np
import re

csv_separator = ';'
val_moral_damage_preprocessed_column_name = '#VALOR_DANO_MORAL_PREPROCESSED'
val_material_damage_preprocessed_column_name = '#VALOR_REEMBOLSO_PREPROCESSED'
minimum_wage_value = 1000

def get_monetary_value_preprocessed(monetary_value):
    monetary_value_preprocessed = ''

    if monetary_value != '':
        minimum_wage_str = re.findall(r'sal.rio[s\- ]+m.n', monetary_value, re.IGNORECASE)
        if len(minimum_wage_str):
            is_specified_in_minimum_wages = True
        else:
            is_specified_in_minimum_wages = False


        monetary_value_match = re.findall(r'^[\( ]*(r\$ )*([ ]*[0-9\. ]+)', monetary_value)

        if (len(monetary_value_match) > 0):
            monetary_value_preprocessed = monetary_value_match[0][1]

            monetary_value_preprocessed = re.sub(r',', '.', monetary_value_preprocessed)
            monetary_value_preprocessed = re.sub(r'[. ]', '', monetary_value_preprocessed)

            if monetary_value_preprocessed != '':
                monetary_value_preprocessed = float(monetary_value_preprocessed)

            if is_specified_in_minimum_wages:
                monetary_value_preprocessed *= minimum_wage_value

    return str(monetary_value_preprocessed)


def preprocess_monetary_values(monetary_value_entries):
    monetary_value_entries_preprocessed = []

    for monetary_value_entry in monetary_value_entries:
        if monetary_value_entry is not np.nan:
            monetary_values = monetary_value_entry.split('\n')
        else:
            monetary_values = ''

        monetary_values_preprocessed = []
        for single_monetary_value in monetary_values:
            single_monetary_value_preprocessed = get_monetary_value_preprocessed(single_monetary_value)

            monetary_values_preprocessed.append(single_monetary_value_preprocessed)

        monetary_values_preprocessed_textual = '\n'.join(monetary_values_preprocessed)

        monetary_value_entries_preprocessed.append(monetary_values_preprocessed_textual)

    return monetary_value_entries_preprocessed


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser('Script to preprocess some columns of the extracted annotations.')

    args_parser.add_argument('extracted_annotations_file_path', help='Path to the file containing the extracted '
                                                                     'annotations.')
    args_parser.add_argument('val_moral_damage_column_name', help='Value of moral damage column name in the file '
                                                                  'containing the extracted annotations.')
    args_parser.add_argument('val_material_damage_column_name', help='Value of material damage column name in the file '
                                                                     'containing the extracted annotations.')
    args_parser.add_argument('output_file_path', help='Path to the output file that will contain the '
                                                      'preprocessed document.')

    args = args_parser.parse_args()

    extracted_annotations_file_path = args.extracted_annotations_file_path
    val_moral_damage_column_name = args.val_moral_damage_column_name
    val_material_damage_column_name = args.val_material_damage_column_name
    output_file_path = args.output_file_path

    print('Loading the extracted annotations from file "%s"...' % extracted_annotations_file_path)
    extracted_annotations = pd.read_csv(extracted_annotations_file_path, sep=csv_separator, header=0, index_col=None)

    assert val_moral_damage_column_name in extracted_annotations.columns, 'Error: column name "%s" not found in file ' \
                                                                          '"%s".' % (val_moral_damage_column_name,
                                                                                     extracted_annotations_file_path)

    assert val_material_damage_column_name in extracted_annotations.columns, 'Error: column name "%s" not found in file ' \
                                                                             '"%s".' % (val_material_damage_column_name,
                                                                                        extracted_annotations_file_path)

    print('Preprocessing column "%s"...' % val_moral_damage_column_name)
    val_moral_damage_entries = extracted_annotations[val_moral_damage_column_name].tolist()
    val_moral_damage_entries_preprocessed = preprocess_monetary_values(val_moral_damage_entries)

    extracted_annotations[val_moral_damage_preprocessed_column_name] = val_moral_damage_entries_preprocessed

    print('Preprocessing column "%s"...' % val_material_damage_column_name)
    val_material_damage_entries = extracted_annotations[val_material_damage_column_name].tolist()
    val_material_damage_entries_preprocessed = preprocess_monetary_values(val_material_damage_entries)

    extracted_annotations[val_material_damage_preprocessed_column_name] = val_material_damage_entries_preprocessed

    print('Saving output file at "%s"...' % output_file_path)
    extracted_annotations.to_csv(output_file_path, sep=csv_separator, header=True, index=False, encoding='utf-8',
                                 quoting=csv.QUOTE_MINIMAL)
