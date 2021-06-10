# -*- coding: utf-8 -*-

import argparse
from textual_dataset import TextualDataset
import conlleval


def get_dataset_statistics(dataset_directory, word_embedding_file_path):
    print("Loading dataset located at '%s'..." % dataset_directory)
    textual_dataset = TextualDataset(word_embedding_file_path=word_embedding_file_path)
    textual_dataset.load(dataset_directory=dataset_directory)

    true_indexes = textual_dataset.Y
    true_indexes = true_indexes.reshape(true_indexes.shape[0], true_indexes.shape[1])

    sentences_sizes = textual_dataset.sentences_sizes

    entity_start = "B-"

    entities_in_documents = {}

    dataset_true_tags = []
    for i in range(len(true_indexes)):
        sentence_true_tags = textual_dataset.get_tags_from_indexes(true_indexes[i][:sentences_sizes[i]])

        document_entities = set([tag for tag in sentence_true_tags if entity_start in tag])

        for document_entity in document_entities:
            if document_entity not in entities_in_documents:
                entities_in_documents[document_entity] = 1
            else:
                entities_in_documents[document_entity] += 1

        dataset_true_tags.extend(sentence_true_tags)

    dataset_num_documents = len(sentences_sizes)
    dataset_num_tokens = sentences_sizes.sum()

    print("-------------------------------------------")
    print("Number of documents of the dataset: %d" % dataset_num_documents)
    print("Number of tokens of the dataset: %d" % dataset_num_tokens)

    print("-------------------------------------------")
    print("Number of documents each entity appeared:")
    for entity, num_documents in entities_in_documents.items():
        print("%s: %d" % (entity.lstrip(entity_start), num_documents))

    print("-------------------------------------------")
    conlleval.evaluate(dataset_true_tags, dataset_true_tags, verbose=True)


if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(description="Script to obtain information about a dataset.")

    args_parser.add_argument('dataset_directory', help='Directory containing dataset files to be read.')
    args_parser.add_argument('word_embedding_file_path', help='File path to the word embedding file.')

    args = args_parser.parse_args()

    dataset_directory = args.dataset_directory
    word_embedding_file_path = args.word_embedding_file_path

    get_dataset_statistics(dataset_directory=dataset_directory, word_embedding_file_path=word_embedding_file_path)
