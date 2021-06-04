import os
import csv
import re


def create_dirs(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def print_parameters(**kwargs):
    for k, v in kwargs.items():
        print("%s = %s" % (k, v))


def write_lines_to_csv(filename, mode, my_list):
    with open(filename, mode, newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=";", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(my_list)


def preprocess_text(text):
    tokens_to_delete = ['', '\n', ' ']

    text_preprocessed = re.split('(\W)', text)
    text_preprocessed_final = list(filter(lambda a: a not in tokens_to_delete, text_preprocessed))

    return text_preprocessed_final
