import pandas as pd
from os import listdir
from os.path import isfile, join, basename
import csv
from gensim.models import KeyedVectors
import re
import numpy as np
import pickle
import util


class TextualDataset():

    def __init__(self, word_embedding_file_path, tag_vocabulary_file_path=None, char_vocabulary_file_path=None,
                 use_char_embedding=False, max_sentence_size=2500, max_word_size=50):

        self.word_column_index = 0
        self.target_column_index = 1
        self.pad_index = 0
        self.unknown_index = 1
        # TODO: change 'O' by 'PAD' when keras.layers.CuDNNLSTM presents support for masking
        self.pad_tag = 'O'
        # Index increment in order to let us use two additional indexes for word: unknown_index and pad_index
        self.word_index_increment = 2
        # Index increment in order to let us use two additional indexes for char: unknown_index and pad_index
        self.char_index_increment = 2
        # Index increment in order to let us use one additional index for tag: pad_index
        self.tag_index_increment = 1

        self.use_char_embedding = use_char_embedding
        self.word_embedding_dimension = None
        self.max_sentence_size = max_sentence_size
        self.max_word_size = max_word_size
        self.files_paths = None
        self.sentences_sizes = None
        self.X = None
        self.X_char = None
        self.Y = None

        assert word_embedding_file_path is not None, "Error: parameter 'word_embedding_file_path' must be supplied."
        self._load_word_embedding(word_embedding_file_path)

        self._load_tag_vocabulary(tag_vocabulary_file_path)

        self._load_char_vocabulary(char_vocabulary_file_path)


    def _load_word_embedding(self, word_embedding_file_path):
        self.word_embedding = KeyedVectors.load_word2vec_format(word_embedding_file_path)
        self.word_embedding_dimension = self.word_embedding.wv.vector_size


    def _load_tag_vocabulary(self, tag_vocabulary_file_path):
        if tag_vocabulary_file_path is None:
            self.tag_vocabulary = {}
            self.index2tag = {}
            self.is_tag_vocabulary_fixed = False
            self.next_tag_index_available = 0
        else:
            with open(tag_vocabulary_file_path, "rb") as file:
                self.tag_vocabulary = pickle.load(file)
                self.index2tag = {value: key for key, value in self.tag_vocabulary.items()}
            self.is_tag_vocabulary_fixed = True


    def _load_char_vocabulary(self, char_vocabulary_file_path):
        if char_vocabulary_file_path is None:
            self.char_vocabulary = {}
            self.index2char = {}
            self.is_char_vocabulary_fixed = False
            self.next_char_index_available = 0
        else:
            with open(char_vocabulary_file_path, "rb") as file:
                self.char_vocabulary = pickle.load(file)
                self.index2char = {value: key for key, value in self.char_vocabulary.items()}
            self.is_char_vocabulary_fixed = True


    def _get_tag_index(self, tag):
        if self.is_tag_vocabulary_fixed:
            tag_index = self.tag_vocabulary[tag]
        else:
            if tag in self.tag_vocabulary:
                tag_index = self.tag_vocabulary[tag]
            else:
                self.tag_vocabulary[tag] = self.next_tag_index_available

                tag_index = self.tag_vocabulary[tag]
                self.index2tag[tag_index] = tag

                self.next_tag_index_available += 1

        return tag_index


    def _get_char_index(self, char):
        if self.is_char_vocabulary_fixed:
            char_index = self.char_vocabulary[char]
        else:
            if char in self.char_vocabulary:
                char_index = self.char_vocabulary[char]
            else:
                self.char_vocabulary[char] = self.next_char_index_available

                char_index = self.char_vocabulary[char]
                self.index2char[char_index] = char

                self.next_char_index_available += 1

        return char_index


    def get_num_tags(self):
        assert self.tag_vocabulary is not None, "Error: cannot get number of tags of an uninitialized vocabulary."
        return len(self.tag_vocabulary) + self.tag_index_increment


    def get_num_chars(self):
        assert self.char_vocabulary is not None, "Error: cannot get number of chars of an uninitialized vocabulary."
        return len(self.char_vocabulary) + self.char_index_increment


    def get_num_words(self):
        assert self.word_embedding is not None, "Error: cannot get number of words of an unitialized word embedding."
        return len(self.word_embedding.vocab) + self.word_index_increment


    def get_tags_from_indexes(self, tag_indexes):
        assert self.tag_vocabulary is not None, "Error: cannot get tags from an uninitialized vocabulary."

        tags = []
        for tag_index in tag_indexes:
            if tag_index == self.pad_index:
                tag = self.pad_tag
            else:
                tag = self.index2tag[tag_index - self.tag_index_increment]

            # TODO: Convert the tags to upper case in the original dataset in order not to need the line below
            tag = tag.upper()

            tags.append(tag)

        return tags


    def get_X(self):
        if self.use_char_embedding:
            return [self.X, self.X_char]
        else:
            return self.X


    def set_Y(self, Y):
        # self.Y = Y.reshape(Y.shape[0], Y.shape[1], 1)
        self.Y = Y


    def _preprocess_word(self, word):
        re_transform_numbers = re.compile(r'\d', re.UNICODE)

        word_preprocessed = re_transform_numbers.sub('0', str(word))

        if len(word_preprocessed) > self.max_word_size:
            word_preprocessed = word_preprocessed[:self.max_word_size]

        return word_preprocessed


    def load(self, dataset_directory):
        self.files_paths = [join(dataset_directory, f) for f in listdir(dataset_directory) if isfile(join(dataset_directory, f))]
        self.sentences_sizes = np.zeros(len(self.files_paths), dtype='int32')

        self.X = np.full((len(self.files_paths), self.max_sentence_size), self.pad_index, dtype='int32')
        self.Y = np.full((len(self.files_paths), self.max_sentence_size), self.pad_index, dtype='int32')

        if self.use_char_embedding:
            self.X_char = np.full((len(self.files_paths), self.max_sentence_size, self.max_word_size), self.pad_index, dtype='int32')

        for i, dataset_file_path in enumerate(self.files_paths):
            dataset_file_content = pd.read_csv(dataset_file_path, sep='\t', quoting=csv.QUOTE_NONE, encoding='utf-8',
                                               header=None, index_col=False)

            assert len(dataset_file_content.columns) == 2, "Error: Document '%s' is illformed." % dataset_file_path

            for current_column in dataset_file_content.columns:
                if current_column == self.word_column_index:

                    for j, word in enumerate(dataset_file_content[current_column]):
                        self.sentences_sizes[i] += 1

                        word_preprocessed = self._preprocess_word(word)

                        word_preprocessed_lower = word_preprocessed.lower()

                        try:
                            word_index = self.word_embedding.vocab[word_preprocessed_lower].index

                            self.X[i,j] = self.word_index_increment + word_index
                        except KeyError:
                            self.X[i,j] = self.unknown_index

                        if self.use_char_embedding:
                            for k, char in enumerate(word_preprocessed):
                                try:
                                    char_index = self._get_char_index(char)

                                    self.X_char[i, j, k] = self.char_index_increment + char_index
                                except KeyError:
                                    self.X_char[i, j, k] = self.unknown_index

                elif current_column == self.target_column_index:
                    for j, tag in enumerate(dataset_file_content[current_column]):
                        tag_index = self._get_tag_index(tag)

                        self.Y[i, j] = self.tag_index_increment + tag_index

        self.Y = self.Y.reshape(self.Y.shape[0], self.Y.shape[1], 1)


    def load_for_prediction(self, dataset_directory):
        self.files_paths = [join(dataset_directory, f) for f in listdir(dataset_directory) if isfile(join(dataset_directory, f))]
        self.sentences_sizes = np.zeros(len(self.files_paths), dtype='int32')

        self.X = np.full((len(self.files_paths), self.max_sentence_size), self.pad_index, dtype='int32')
        self.texts = []

        if self.use_char_embedding:
            self.X_char = np.full((len(self.files_paths), self.max_sentence_size, self.max_word_size), self.pad_index, dtype='int32')

        for i, dataset_file_path in enumerate(self.files_paths):
            dataset_file_content = pd.read_csv(dataset_file_path, sep='\t', quoting=csv.QUOTE_NONE, encoding='utf-8',
                                               header=None, index_col=False)

            # assert len(dataset_file_content.columns) == 1, "Error: Document '%s' is illformed." % dataset_filename

            for current_column in dataset_file_content.columns:
                if current_column == self.word_column_index:
                    self.texts.append(dataset_file_content[current_column].to_list())

                    for j, word in enumerate(dataset_file_content[current_column]):
                        self.sentences_sizes[i] += 1

                        word_preprocessed = self._preprocess_word(word)

                        word_preprocessed_lower = word_preprocessed.lower()

                        try:
                            word_index = self.word_embedding.vocab[word_preprocessed_lower].index

                            self.X[i,j] = self.word_index_increment + word_index
                        except KeyError:
                            self.X[i,j] = self.unknown_index

                        if self.use_char_embedding:
                            for k, char in enumerate(word_preprocessed):
                                if char in self.char_vocabulary:
                                    char_index = self.char_index_increment + self._get_char_index(char)
                                else:
                                    char_index = self.unknown_index

                                self.X_char[i,j,k] = char_index


    def save(self, output_directory):
        for i in range(len(self.X)):
            current_filename = basename(self.files_paths[i])
            current_sentence_size = self.sentences_sizes[i]
            current_text = self.texts[i]
            current_Y = self.Y[i]

            current_tags = self.get_tags_from_indexes(current_Y[:current_sentence_size])

            assert len(current_text) == len(current_tags), "Error: number of words is different from the number of tags."

            data = pd.DataFrame(list(zip(current_text, current_tags)))

            current_file_path = join(output_directory, current_filename)

            data.to_csv(current_file_path, sep='\t', quoting=csv.QUOTE_NONE, encoding='utf-8',
                        header=False, index=False)


    def save_in_one_single_file(self, output_directory):
        output_filename = "extracted_annotations.csv"
        output_file_path = join(output_directory, output_filename)

        target_entities_names = self.get_sorted_target_entities_names()

        header = ['Filename', *target_entities_names]

        util.write_lines_to_csv(output_file_path, 'w', [header])

        csv_writing_interval = 10
        documents_records = []

        for i in range(len(self.X)):
            current_filename = basename(self.files_paths[i])
            current_sentence_size = self.sentences_sizes[i]
            current_text = self.texts[i]
            current_Y = self.Y[i]

            current_tags = self.get_tags_from_indexes(current_Y[:current_sentence_size])

            assert len(current_text) == len(current_tags), "Error: number of words is different from the number of tags."

            annotated_entities = self.get_annotated_entities(current_text, current_tags, target_entities_names)

            document_record = [current_filename, *annotated_entities]

            documents_records.append(document_record)

            if len(documents_records) == csv_writing_interval:
                util.write_lines_to_csv(output_file_path, 'a', documents_records)

                documents_records = []

        if len(documents_records) > 0:
            util.write_lines_to_csv(output_file_path, 'a', documents_records)


    def get_annotated_entities(self, text, tags, target_entities_names):
        entities_values = [None] * len(target_entities_names)

        entities_texts = self.get_entities_texts(text, tags)

        for i, target_entity_name in enumerate(target_entities_names):
            if target_entity_name in entities_texts:
                current_target_entity = entities_texts[target_entity_name]
                entities_values[i] = '\n'.join(current_target_entity)

        return entities_values


    def get_entities_texts(self, text, tags):
        entities_records = {}
        entities_indexes = self.get_entities_indexes(tags)

        for entity_name, start_end_indexes in entities_indexes.items():
            entity_entries = []
            for start_end_index in start_end_indexes:
                assert len(start_end_index) == 2, "Error: expecting start and end indexes."

                entity_text = text[start_end_index[0]: start_end_index[1] + 1]
                entity_text_joined = ' '.join(entity_text)

                entity_entries.append(entity_text_joined)

            entities_records[entity_name] = entity_entries

        return entities_records


    def get_entities_indexes(self, iob_sequence):
        entity_dict = {}

        start_index = -1
        end_index = -1
        tag_to_dict = ""
        is_there_new_entity_in_sequence = False
        last_tag = "  "
        for i, tag in enumerate(iob_sequence):
            if len(tag) > 1:
                if tag[:2] in ["B-", "b-"]:
                #if tag[2:] != last_tag[2:]:
                    if start_index == -1:
                        start_index = i
                        tag_to_dict = tag[2:]
                    else:
                        end_index = i - 1
                        is_there_new_entity_in_sequence = True

            elif tag in ["O", "o"] and start_index != -1:
                end_index = i - 1

            if start_index != -1 and end_index != -1:
                if tag_to_dict not in entity_dict:
                    entity_dict[tag_to_dict] = []

                entity_dict[tag_to_dict].append((start_index, end_index))

                if is_there_new_entity_in_sequence:
                    start_index = i
                    tag_to_dict = tag[2:]
                else:
                    start_index = -1
                    tag_to_dict = ""

                end_index = -1
                is_there_new_entity_in_sequence = False

            last_tag = tag

        return entity_dict


    def get_sorted_target_entities_names(self):
        assert self.tag_vocabulary is not None, "Error: target vocabulary cannot be null."

        iob_tags = self.tag_vocabulary.keys()
        entity_name_set = set()

        for iob_tag in iob_tags:
            if len(iob_tag) > 1:
                if iob_tag[0:2].lower() in ["b-", "i-"]:
                    tag = iob_tag[2:]

                    # TODO: Convert the tags to upper case in the original dataset in order not to need the line below
                    tag = tag.upper()

                    entity_name_set.add(tag)

        sorted_entity_names = sorted(list(entity_name_set))

        return sorted_entity_names


    def save_vocabularies(self, tag_vocabulary_file_path, char_vocabulary_file_path):
        with open(tag_vocabulary_file_path, "wb") as file:
            pickle.dump(self.tag_vocabulary, file)

        with open(char_vocabulary_file_path, "wb") as file:
            pickle.dump(self.char_vocabulary, file)


    def get_weights_matrix(self):
        weights_matrix = np.random.random((self.get_num_words(), self.word_embedding_dimension))

        for word, info in self.word_embedding.vocab.items():
            word_index = self.word_index_increment + info.index
            weights_matrix[word_index] = self.word_embedding.get_vector(word)

        return weights_matrix
