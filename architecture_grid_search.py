# -*- coding: utf-8 -*-

from os import listdir
from os.path import isfile, join, basename
import pickle
import argparse
from tagger import Tagger
from textual_dataset import TextualDataset
from keras.layers import Bidirectional, CuDNNLSTM, TimeDistributed, Dense, Input, Embedding, Dropout, SpatialDropout1D, concatenate
from keras import Model
from keras.optimizers import RMSprop
from keras_contrib.layers import CRF
from keras_contrib.losses import crf_loss
from itertools import product


### Configures Tensorflow not allocate the whole memory initially - Beginning
import tensorflow as tf
from keras import backend as k

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
k.tensorflow_backend.set_session(tf.compat.v1.Session(config=config))
### Configures Tensorflow not allocate the whole memory initially - End


def define_model(dataset, use_char_embedding, max_word_size, loss, learning_rate, dropout_rate, state=0):
    assert dataset is not None, "Error: 'dataset' cannot be 'None' when defining a model architecture."
    assert state >= 0, "Error: 'state' cannot be negative."

    candidate_units_first_layer = [128, 64, 32, None]
    candidate_units_second_layer = [128, 64, 32]
    candidate_crf_values = [True, False]

    char_embedding_candidate_units_first_layer = [16]
    char_embedding_candidate_units_second_layer = [16]
    char_embedding_candidate_dimension = [20]

    if not use_char_embedding:
        char_embedding_candidate_units_first_layer = [None]
        char_embedding_candidate_units_second_layer = [None]
        char_embedding_candidate_dimension = [None]

    combination_architectures = product(candidate_units_first_layer, candidate_units_second_layer, candidate_crf_values, \
                                        char_embedding_candidate_units_first_layer, char_embedding_candidate_units_second_layer, \
                                        char_embedding_candidate_dimension)

    original_loss = loss

    current_state = -1
    for num_units_first_layer, num_units_second_layer, use_crf, char_embedding_num_units_first_layer, \
           char_embedding_num_units_second_layer, char_embedding_dimension in combination_architectures:

        current_state += 1

        if current_state < state:
            continue

        ### Word definition - Beginning
        word_input = Input(shape=(dataset.max_sentence_size, ), dtype='int32')

        word_embedding = Embedding(dataset.get_num_words(), dataset.word_embedding_dimension, weights=[dataset.get_weights_matrix()],
                                   input_length=dataset.max_sentence_size, trainable=False, mask_zero=False)(word_input)
        ### Word definition - End

        if use_char_embedding:
            ### Char definition - Beginning
            char_input = Input(shape=(dataset.max_sentence_size, dataset.max_word_size, ), dtype='int32')

            char_embedding = TimeDistributed(Embedding(dataset.get_num_chars(), char_embedding_dimension,
                                                       input_length=dataset.max_word_size, mask_zero=False))(char_input)

            char_encoded = Dropout(dropout_rate)(char_embedding)

            if char_embedding_num_units_first_layer is not None:
                char_encoded = TimeDistributed(Bidirectional(CuDNNLSTM(units=char_embedding_num_units_first_layer, return_sequences=True)))(char_encoded)
                char_encoded = Dropout(dropout_rate)(char_encoded)

            char_encoded = TimeDistributed(Bidirectional(CuDNNLSTM(units=char_embedding_num_units_second_layer, return_sequences=False)))(char_encoded)
            ### Char definition - End

            embedding = concatenate([word_embedding, char_encoded])
        else:
            embedding = word_embedding

        x = SpatialDropout1D(dropout_rate)(embedding)

        if num_units_first_layer is not None:
            x = Bidirectional(CuDNNLSTM(units=num_units_first_layer, return_sequences=True))(x)
            x = Dropout(dropout_rate)(x)

        x = Bidirectional(CuDNNLSTM(units=num_units_second_layer, return_sequences=True))(x)

        if not use_crf:
            predictions = TimeDistributed(Dense(dataset.get_num_tags(), activation="softmax"))(x)

            loss = original_loss
        else:
            x = TimeDistributed(Dense(dataset.get_num_tags(), activation="relu"))(x)
            predictions = CRF(dataset.get_num_tags(), sparse_target=True)(x)

            loss = crf_loss

        if use_char_embedding:
            model = Model(inputs=[word_input, char_input], outputs=predictions)
        else:
            model = Model(inputs=word_input, outputs=predictions)

        rmsprop_optim = RMSprop(lr=learning_rate)
        model.compile(optimizer=rmsprop_optim, loss=loss)

        yield model


def train_cv_on_architectures(dataset_directory, word_embeddings_directory, state_directory, tag_vocabulary_file_path,
                              char_vocabulary_file_path, use_char_embedding, plot_file_path_prefix, model_state_filename,
                              max_word_size, batch_size, num_epochs, learning_rate, dropout_rate, loss, num_folds,
                              random_state_seed, verbose):

    word_embeddings_files_paths = [join(word_embeddings_directory, f) for f in listdir(word_embeddings_directory) if isfile(join(word_embeddings_directory, f))]

    for word_embedding_file_path in word_embeddings_files_paths:

        word_embedding_filename = basename(word_embedding_file_path)
        word_embedding_state_file_path = join(state_directory, word_embedding_filename)
        model_state_file_path = join(state_directory, word_embedding_filename.rstrip(".txt") + "_" + model_state_filename)


        if isfile(word_embedding_state_file_path):
            continue

        if isfile(model_state_file_path):
            with open(model_state_file_path, "rb") as file:
                model_state = pickle.load(file)
        else:
            model_state = 0

        print("\n******************************")
        print("Start processing word embedding located at '%s'..." % word_embedding_file_path)

        print("Loading dataset...")
        textual_dataset = TextualDataset(word_embedding_file_path=word_embedding_file_path,
                                         use_char_embedding=use_char_embedding,
                                         max_word_size=max_word_size)
        textual_dataset.load(dataset_directory=dataset_directory)

        print("Saving tag vocabulary...")
        textual_dataset.save_vocabularies(tag_vocabulary_file_path=tag_vocabulary_file_path,
                                          char_vocabulary_file_path=char_vocabulary_file_path)

        print("Start running model architectures...")
        for model in define_model(dataset=textual_dataset, use_char_embedding=use_char_embedding,
                                  max_word_size=max_word_size, loss=loss, learning_rate=learning_rate,
                                  dropout_rate=dropout_rate, state=model_state):

            print("Model (%d) architecture..." % (model_state + 1))
            model.summary()

            plot_file_path_prefix_local = "%s%s_model%d_" % (plot_file_path_prefix,
                                                             word_embedding_filename.rstrip(".txt"),
                                                             model_state + 1)
            best_model_temp_file_name = "%s_model%d.bin" % (word_embedding_filename.rstrip(".txt"), model_state + 1)
            best_model_temp_file_path = join(state_directory, best_model_temp_file_name)

            print("Plot files prefix: '%s'" % plot_file_path_prefix_local)

            print("Starting cross-validation...")
            tagger = Tagger(dataset=textual_dataset, model=model)
            tagger.train_cv(num_epochs=num_epochs, num_folds=num_folds, batch_size=batch_size,
                            random_state_seed=random_state_seed, plot_file_path_prefix=plot_file_path_prefix_local,
                            best_model_temp_file_path=best_model_temp_file_path, verbose=verbose)

            # Updates the 'model_state' to the next number
            model_state += 1

            # Updates the model state file, in order to resume the execution if any problem happens
            with open(model_state_file_path, "wb") as file:
                pickle.dump(model_state, file)

        print("End of execution of model architectures for word embedding '%s'" % word_embedding_file_path)

        # Creates a state file, indicating the execution of the current word embedding is done
        with open(word_embedding_state_file_path, 'w') as file:
            file.write('')


if __name__ == '__main__':
    batch_size = 32
    num_epochs = 60
    learning_rate = 0.01
    dropout_rate = 0.1
    loss = 'sparse_categorical_crossentropy'
    num_folds = 5
    random_state_seed = 1
    model_state_filename = 'current_model_state.pickle'

    args_parser = argparse.ArgumentParser(description='Script to find the best combination of word embedding and '
                                                      'neural network architecture, trained and evaluated '
                                                      'through cross-validation.')

    args_parser.add_argument('word_embeddings_directory', help='Directory that contains several word embeddings '
                                                               'files to be used to train models.')
    args_parser.add_argument('dataset_directory', help='Directory that contains the dataset files to be used '
                                                       'to train models.')
    args_parser.add_argument('state_directory', help='Directory that contains the state files to be used '
                                                       'when resuming execution.')
    args_parser.add_argument('tag_vocabulary_file_path', help='File path to the file containg the tag vocabulary.')
    args_parser.add_argument('char_vocabulary_file_path', help='File path to the file containing the char vocabulary.')
    args_parser.add_argument('plot_file_path_prefix', help='Path prefix for the plot files.')
    args_parser.add_argument('-e', '--use_char_embedding', type=int, choices=[0, 1], default=0, help='Indicates whether '
                                                                                                     'char embedding is '
                                                                                                     'going to be used.')
    args_parser.add_argument('-m', '--max_word_size', type=int, default=10, help='In case of using char embedding, '
                                                                                 'represents the maximum word size.')
    args_parser.add_argument('-vv', '--verbose', action='count', default=0, help='Indicates whether turn on verbose mode.')

    args = args_parser.parse_args()

    dataset_directory = args.dataset_directory
    word_embeddings_directory = args.word_embeddings_directory
    state_directory = args.state_directory
    tag_vocabulary_file_path = args.tag_vocabulary_file_path
    char_vocabulary_file_path = args.char_vocabulary_file_path
    plot_file_path_prefix = args.plot_file_path_prefix
    use_char_embedding = bool(args.use_char_embedding)
    max_word_size = args.max_word_size
    verbose = bool(args.verbose)

    train_cv_on_architectures(dataset_directory=dataset_directory, word_embeddings_directory=word_embeddings_directory,
                              state_directory=state_directory, tag_vocabulary_file_path=tag_vocabulary_file_path,
                              char_vocabulary_file_path=char_vocabulary_file_path, use_char_embedding=use_char_embedding,
                              plot_file_path_prefix=plot_file_path_prefix, model_state_filename=model_state_filename,
                              max_word_size=max_word_size, batch_size=batch_size, num_epochs=num_epochs,
                              learning_rate=learning_rate, dropout_rate=dropout_rate, loss=loss, num_folds=num_folds,
                              random_state_seed=random_state_seed, verbose=verbose)
