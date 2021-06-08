# -*- coding: utf-8 -*-

import argparse
from tagger import Tagger
from textual_dataset import TextualDataset
from keras.layers import Bidirectional, CuDNNLSTM, TimeDistributed, Dense, Input, Embedding, Dropout, SpatialDropout1D, concatenate

from keras import Model
from keras.optimizers import RMSprop
from keras_contrib.layers import CRF
from keras_contrib.losses import crf_loss
import sys


### Configures Tensorflow not allocate the whole memory initially - Beginning
import tensorflow as tf
from keras import backend as k

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
k.tensorflow_backend.set_session(tf.compat.v1.Session(config=config))
### Configures Tensorflow not allocate the whole memory initially - End


def define_model(dataset, num_units_first_layer, num_units_second_layer, 
                 char_embedding_num_units_first_layer, char_embedding_num_units_second_layer,
                 char_embedding_dimension, use_crf, use_char_embedding,
                 max_word_size, loss, learning_rate, dropout_rate):
    assert dataset is not None, "Error: 'dataset' cannot be 'None' when defining a model architecture."

    ### Word definition - Beginning
    word_input = Input(shape=(dataset.max_sentence_size,), dtype='int32')

    word_embedding = Embedding(dataset.get_num_words(), dataset.word_embedding_dimension,
                               weights=[dataset.get_weights_matrix()],
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

    return model


def train(dataset_directory, word_embedding_file_path, model_file_path, tag_vocabulary_file_path,
          char_vocabulary_file_path, use_char_embedding, num_units_first_layer, num_units_second_layer,
          char_embedding_num_units_first_layer, char_embedding_num_units_second_layer,
          char_embedding_dimension, use_crf, max_word_size, batch_size, num_epochs, loss, 
          learning_rate, dropout_rate, verbose):

    print("Loading dataset...")
    textual_dataset = TextualDataset(word_embedding_file_path=word_embedding_file_path,
                                     use_char_embedding=use_char_embedding,
                                     max_word_size=max_word_size)
    textual_dataset.load(dataset_directory=dataset_directory)

    print("Saving tag vocabulary...")
    textual_dataset.save_vocabularies(tag_vocabulary_file_path=tag_vocabulary_file_path,
                                      char_vocabulary_file_path=char_vocabulary_file_path)

    print("Defining model architecture...")
    model = define_model(dataset=textual_dataset, num_units_first_layer=num_units_first_layer,
                         num_units_second_layer=num_units_second_layer, 
                         char_embedding_num_units_first_layer=char_embedding_num_units_first_layer,
                         char_embedding_num_units_second_layer=char_embedding_num_units_second_layer,
                         char_embedding_dimension=char_embedding_dimension, use_crf=use_crf,
                         use_char_embedding=use_char_embedding, max_word_size=max_word_size,
                         loss=loss, learning_rate=learning_rate, dropout_rate=dropout_rate)

    print("Model architecture...")
    model.summary()

    print("Training model...")
    tagger = Tagger(dataset=textual_dataset, model=model)
    tagger.train(num_epochs=num_epochs, batch_size=batch_size, verbose=verbose)

    print("Saving trained model...")
    tagger.save_model(model_file_path)


def train_cv(dataset_directory, word_embedding_file_path, tag_vocabulary_file_path, char_vocabulary_file_path,
             use_char_embedding, plot_file_path_prefix, num_units_first_layer, num_units_second_layer,
             char_embedding_num_units_first_layer, char_embedding_num_units_second_layer,
             char_embedding_dimension, use_crf, max_word_size, batch_size, num_epochs, loss, 
             learning_rate, dropout_rate, num_folds, random_state_seed, verbose):

    print("Loading dataset...")
    textual_dataset = TextualDataset(word_embedding_file_path=word_embedding_file_path,
                                     use_char_embedding=use_char_embedding,
                                     max_word_size=max_word_size)
    textual_dataset.load(dataset_directory=dataset_directory)

    print("Saving tag vocabulary...")
    textual_dataset.save_vocabularies(tag_vocabulary_file_path=tag_vocabulary_file_path,
                                      char_vocabulary_file_path=char_vocabulary_file_path)

    print("Defining model architecture...")
    model = define_model(dataset=textual_dataset, num_units_first_layer=num_units_first_layer,
                         num_units_second_layer=num_units_second_layer, 
                         char_embedding_num_units_first_layer=char_embedding_num_units_first_layer,
                         char_embedding_num_units_second_layer=char_embedding_num_units_second_layer,
                         char_embedding_dimension=char_embedding_dimension, use_crf=use_crf,
                         use_char_embedding=use_char_embedding, max_word_size=max_word_size,
                         loss=loss, learning_rate=learning_rate, dropout_rate=dropout_rate)

    print("Model architecture...")
    model.summary()

    print("Starting cross-validation...")
    tagger = Tagger(dataset=textual_dataset, model=model)
    tagger.train_cv(num_epochs=num_epochs, num_folds=num_folds, batch_size=batch_size,
                    random_state_seed=random_state_seed, plot_file_path_prefix=plot_file_path_prefix, verbose=verbose)


def evaluate(dataset_directory, word_embedding_file_path, model_file_path, tag_vocabulary_file_path,
             char_vocabulary_file_path, use_char_embedding, max_word_size, verbose):

    print("Loading dataset...")
    textual_dataset = TextualDataset(word_embedding_file_path=word_embedding_file_path,
                                     tag_vocabulary_file_path=tag_vocabulary_file_path,
                                     char_vocabulary_file_path=char_vocabulary_file_path,
                                     use_char_embedding=use_char_embedding,
                                     max_word_size=max_word_size)
    textual_dataset.load(dataset_directory=dataset_directory)

    print("Loading model...")
    tagger = Tagger(dataset=textual_dataset)
    tagger.load_model(model_file_path=model_file_path)

    print("Evaluating model on loaded dataset...")
    quality = tagger.evaluate(verbose=verbose)

    print("Model quality")
    for metric, value in quality.items():
        print("%s: %.2f percent" % (metric, value))


def predict(dataset_directory, predictions_directory, word_embedding_file_path, model_file_path,
            tag_vocabulary_file_path, char_vocabulary_file_path, use_char_embedding,
            max_word_size):

    print("Loading dataset...")
    textual_dataset = TextualDataset(word_embedding_file_path=word_embedding_file_path,
                                     tag_vocabulary_file_path=tag_vocabulary_file_path,
                                     char_vocabulary_file_path=char_vocabulary_file_path,
                                     use_char_embedding=use_char_embedding,
                                     max_word_size=max_word_size)
    textual_dataset.load_for_prediction(dataset_directory=dataset_directory)

    print("Loading model...")
    tagger = Tagger(dataset=textual_dataset)
    tagger.load_model(model_file_path=model_file_path)

    print("Generating predictions...")
    tagger.predict(predictions_directory=predictions_directory)


if __name__ == "__main__":
    num_units_first_layer = 32
    num_units_second_layer = 32

    char_embedding_num_units_first_layer = 16
    char_embedding_num_units_second_layer = 16
    char_embedding_dimension = 20

    batch_size = 32
    num_epochs = 60
    learning_rate = 0.01
    dropout_rate = 0.1
    loss = 'sparse_categorical_crossentropy'
    num_folds = 5
    random_state_seed = 1

    args_parser = argparse.ArgumentParser("Script to train, evaluate and predict a named entity model.")

    args_parser.add_argument('action', choices=['train', 'train_cv', 'evaluate', 'predict', 'usage'], help='')
    args_parser.add_argument('-d', '--dataset_directory', help='Directory containing dataset files to perform the specified '
                                                               'action.')
    args_parser.add_argument('-v', '--validation_set_directory', help='Directory containing files to perform the validation of '
                                                                      'the model to be trained.')
    args_parser.add_argument('-p', '--predictions_directory', help='Directory to save the predicted files.')
    args_parser.add_argument('-w', '--word_embedding_file_path', help='File path to the word embedding file.')
    args_parser.add_argument('-t', '--tag_vocabulary_file_path', help='File path to the file containing the tag vocabulary.')
    args_parser.add_argument('-c', '--char_vocabulary_file_path', help='File path to the file containing the char vocabulary.')
    args_parser.add_argument('-m', '--model_file_path', help='File path to the model file.')
    args_parser.add_argument('-f', '--plot_file_path_prefix', help='Path prefix for the plot files.')
    args_parser.add_argument('-e', '--use_char_embedding', type=int, choices=[0, 1], default=0, help='Indicates whether char '
                                                                                                     'embedding is going '
                                                                                                     'to be used.')
    args_parser.add_argument('-s', '--use_crf', type=int, choices=[0, 1], default=0, help='Indicates whether a CRF model '
                                                                                          'is going to be stacked over '
                                                                                          'neural network output.')
    args_parser.add_argument('-m', '--max_word_size', type=int, default=10, help='In case of using char embedding, '
                                                                                 'represents the maximum word size.')
    args_parser.add_argument('-vv', '--verbose', action='count', default=0, help='Indicates whether turn on verbose mode.')

    args = args_parser.parse_args()

    dataset_directory = args.dataset_directory
    validation_set_directory = args.validation_set_directory
    predictions_directory = args.predictions_directory
    word_embedding_file_path = args.word_embedding_file_path
    tag_vocabulary_file_path = args.tag_vocabulary_file_path
    char_vocabulary_file_path = args.char_vocabulary_file_path
    model_file_path = args.model_file_path
    plot_file_path_prefix = args.plot_file_path_prefix
    use_char_embedding = bool(args.use_char_embedding)
    use_crf = bool(args.use_crf)
    max_word_size = args.max_word_size
    verbose = bool(args.verbose)

    if args.action == "train":
        train(dataset_directory=dataset_directory, word_embedding_file_path=word_embedding_file_path,
              model_file_path=model_file_path, tag_vocabulary_file_path=tag_vocabulary_file_path,
              char_vocabulary_file_path=char_vocabulary_file_path, use_char_embedding=use_char_embedding,
              num_units_first_layer=num_units_first_layer, num_units_second_layer=num_units_second_layer,
              char_embedding_num_units_first_layer=char_embedding_num_units_first_layer,
              char_embedding_num_units_second_layer=char_embedding_num_units_second_layer,
              char_embedding_dimension=char_embedding_dimension,
              use_crf=use_crf, max_word_size=max_word_size, batch_size=batch_size, num_epochs=num_epochs,
              learning_rate=learning_rate, loss=loss, dropout_rate=dropout_rate, verbose=verbose)

        if validation_set_directory is not None:
            print("Quality on validation dataset")
            evaluate(dataset_directory=validation_set_directory, word_embedding_file_path=word_embedding_file_path,
                     model_file_path=model_file_path, tag_vocabulary_file_path=tag_vocabulary_file_path,
                     char_vocabulary_file_path=char_vocabulary_file_path, use_char_embedding=use_char_embedding,
                     verbose=verbose)

    elif args.action == "train_cv":
        train_cv(dataset_directory=dataset_directory, word_embedding_file_path=word_embedding_file_path,
                 tag_vocabulary_file_path=tag_vocabulary_file_path, char_vocabulary_file_path=char_vocabulary_file_path,
                 use_char_embedding=use_char_embedding, plot_file_path_prefix=plot_file_path_prefix,
                 num_units_first_layer=num_units_first_layer, num_units_second_layer=num_units_second_layer,
                 char_embedding_num_units_first_layer=char_embedding_num_units_first_layer,
                 char_embedding_num_units_second_layer=char_embedding_num_units_second_layer,
                 char_embedding_dimension=char_embedding_dimension,
                 use_crf=use_crf, max_word_size=max_word_size, batch_size=batch_size, num_epochs=num_epochs,
                 learning_rate=learning_rate, loss=loss, dropout_rate=dropout_rate, num_folds=num_folds,
                 random_state_seed=random_state_seed, verbose=verbose)

    elif args.action == "evaluate":
        evaluate(dataset_directory=dataset_directory, word_embedding_file_path=word_embedding_file_path,
                 model_file_path=model_file_path, tag_vocabulary_file_path=tag_vocabulary_file_path,
                 char_vocabulary_file_path=char_vocabulary_file_path, use_char_embedding=use_char_embedding,
                 verbose=verbose)

    elif args.action == "predict":
        predict(dataset_directory=dataset_directory, predictions_directory=predictions_directory,
                word_embedding_file_path=word_embedding_file_path, model_file_path=model_file_path,
                tag_vocabulary_file_path=tag_vocabulary_file_path, char_vocabulary_file_path=char_vocabulary_file_path,
                use_char_embedding=use_char_embedding)

    elif args.action == "usage":
        script_filename = sys.argv[0]

        detailed_usage = """
Below we present some use cases of this script.
(i) To train a model:
\t{} train -d data/training_files/ -v data/validation_files/ -w data/word2vec.txt -t data/tag_vocabulary.pickle -e 1 -c data/char_vocabulary.pickle -m out/model.bin
The command line above is going to train a model, creating three new files, data/tag_vocabulary.pickle, data/char_vocabulary.pickle and out/model.bin.
(ii) To cross-validate a model:
\t{} train_cv -d data/cross_validation_files/ -w data/word2vec.txt -t data/tag_vocabulary.pickle -e 1 -c data/char_vocabulary.pickle
The command line above is going to cross-validate a model, creating two new files, data/tag_vocabulary.pickle and data/char_vocabulary.pickle.
(iii) To evaluate a model:
\t{} evaluate -d data/test_files/ -w data/word2vec.txt -t data/tag_vocabulary.pickle -e 1 -c data/char_vocabulary.pickle -m out/model.bin
The command line above is going to evaluate an existing model, reading the three files previously created, data/tag_vocabulary.pickle, data/char_vocabulary.pickle and out/model.bin.
(iv) To predict with a model:
\t{} predict -d data/unclassified_files/ -p out/predicted_files/ -w data/word2vec.txt -t data/tag_vocabulary.pickle -e 1 -c data/char_vocabulary.pickle -m out/model.bin
The command line above is going to generate predictions using an existing model, reading the three files previously created, data/tag_vocabulary.pickle, data/char_vocabulary.pickle and out/model.bin, and saving the predicted files in out/predicted_files/ directory.
""".format(script_filename, script_filename, script_filename, script_filename)

        print(detailed_usage)
