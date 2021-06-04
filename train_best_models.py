# -*- coding: utf-8 -*-

from os.path import isfile
from tagger import Tagger
from textual_dataset import TextualDataset
from main import train


### Configures Tensorflow not allocate the whole memory initially - Beginning
import tensorflow as tf
from keras import backend as k

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
k.tensorflow_backend.set_session(tf.compat.v1.Session(config=config))
### Configures Tensorflow not allocate the whole memory initially - End


def evaluate(dataset_directory, word_embedding_file_path, model_file_path, tag_vocabulary_file_path,
             char_vocabulary_file_path, use_char_embedding, verbose):

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


if __name__ == "__main__":
    batch_size = 32
    learning_rate = 0.01
    dropout_rate = 0.1
    loss = 'sparse_categorical_crossentropy'
    verbose = True

    word_embedding_file_path = 'data/best_word_embedding/word2vec_skipgram_s100.txt'

    execution_lines = []

    ######### BILSTM-CE-CRF best models beginning ##############

    ######### KP Primeira Instancia ###############
    # Model 21
    execution_line = {
        'char_embedding_num_units_first_layer': 16,
        'char_embedding_num_units_second_layer': 16,
        'char_embedding_dimension': 20,
        'num_units_first_layer': None,
        'num_units_second_layer': 64,
        'use_crf': True,
        'num_epochs': 32,
        'dataset_directory': 'data/kp_primeira_instancia/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_primeira_instancia_bilstmcecrf.pickle',
        'use_char_embedding': True,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_primeira_instancia_bilstmcecrf.pickle',
        'model_file_path': 'out/model_kp_primeira_instancia_bilstmcecrf.bin',
        'max_word_size': 62
    }
    execution_lines.append(execution_line)

    ######### KP Relatorios ###############
    # Model 7
    execution_line = {
        'char_embedding_num_units_first_layer': 16,
        'char_embedding_num_units_second_layer': 16,
        'char_embedding_dimension': 20,
        'num_units_first_layer': 64,
        'num_units_second_layer': 128,
        'use_crf': True,
        'num_epochs': 56,
        'dataset_directory': 'data/kp_relatorios/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_relatorios_bilstmcecrf.pickle',
        'use_char_embedding': True,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_relatorios_bilstmcecrf.pickle',
        'model_file_path': 'out/model_kp_relatorios_bilstmcecrf.bin',
        'max_word_size': 68
    }
    execution_lines.append(execution_line)

    ######### KP Segunda Instancia ###############
    # Model 11
    execution_line = {
        'char_embedding_num_units_first_layer': 16,
        'char_embedding_num_units_second_layer': 16,
        'char_embedding_dimension': 20,
        'num_units_first_layer': 64,
        'num_units_second_layer': 32,
        'use_crf': True,
        'num_epochs': 11,
        'dataset_directory': 'data/kp_segunda_instancia/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_segunda_instancia_bilstmcecrf.pickle',
        'use_char_embedding': True,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_segunda_instancia_bilstmcecrf.pickle',
        'model_file_path': 'out/model_kp_segunda_instancia_bilstmcecrf.bin',
        'max_word_size': 52
    }
    execution_lines.append(execution_line)

    ######### BILSTM-CE-CRF best models end ##############


    ######### BILSTM-CE best models beginning ##############

    ######### KP Primeira Instancia ###############
    # Model 18
    execution_line = {
        'char_embedding_num_units_first_layer': 16,
        'char_embedding_num_units_second_layer': 16,
        'char_embedding_dimension': 20,
        'num_units_first_layer': 32,
        'num_units_second_layer': 32,
        'use_crf': False,
        'num_epochs': 5,
        'dataset_directory': 'data/kp_primeira_instancia/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_primeira_instancia_bilstmce.pickle',
        'use_char_embedding': True,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_primeira_instancia_bilstmce.pickle',
        'model_file_path': 'out/model_kp_primeira_instancia_bilstmce.bin',
        'max_word_size': 62
    }
    execution_lines.append(execution_line)

    ######### KP Relatorios ###############
    # Model 10
    execution_line = {
        'char_embedding_num_units_first_layer': 16,
        'char_embedding_num_units_second_layer': 16,
        'char_embedding_dimension': 20,
        'num_units_first_layer': 64,
        'num_units_second_layer': 64,
        'use_crf': False,
        'num_epochs': 4,
        'dataset_directory': 'data/kp_relatorios/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_relatorios_bilstmce.pickle',
        'use_char_embedding': True,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_relatorios_bilstmce.pickle',
        'model_file_path': 'out/model_kp_relatorios_bilstmce.bin',
        'max_word_size': 68
    }

    execution_lines.append(execution_line)

    ######### KP Segunda Instancia ###############
    # Model 2
    execution_line = {
        'char_embedding_num_units_first_layer': 16,
        'char_embedding_num_units_second_layer': 16,
        'char_embedding_dimension': 20,
        'num_units_first_layer': 128,
        'num_units_second_layer': 128,
        'use_crf': False,
        'num_epochs': 6,
        'dataset_directory': 'data/kp_segunda_instancia/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_segunda_instancia_bilstmce.pickle',
        'use_char_embedding': True,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_segunda_instancia_bilstmce.pickle',
        'model_file_path': 'out/model_kp_segunda_instancia_bilstmce.bin',
        'max_word_size': 52
    }
    execution_lines.append(execution_line)

    ######### BILSTM-CE best models end ##############


    ######### BILSTM-CRF best models beginning ##############

    ######### KP Primeira Instancia ###############
    # Model 7
    execution_line = {
        'char_embedding_num_units_first_layer': None,
        'char_embedding_num_units_second_layer': None,
        'char_embedding_dimension': None,
        'num_units_first_layer': 64,
        'num_units_second_layer': 128,
        'use_crf': True,
        'num_epochs': 32,
        'dataset_directory': 'data/kp_primeira_instancia/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_primeira_instancia_bilstmcrf.pickle',
        'use_char_embedding': False,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_primeira_instancia_bilstmcrf.pickle',
        'model_file_path': 'out/model_kp_primeira_instancia_bilstmcrf.bin',
        'max_word_size': 62
    }
    execution_lines.append(execution_line)

    ######### KP Relatorios ###############
    # Model 13
    execution_line = {
        'char_embedding_num_units_first_layer': None,
        'char_embedding_num_units_second_layer': None,
        'char_embedding_dimension': None,
        'num_units_first_layer': 32,
        'num_units_second_layer': 128,
        'use_crf': True,
        'num_epochs': 24,
        'dataset_directory': 'data/kp_relatorios/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_relatorios_bilstmcrf.pickle',
        'use_char_embedding': False,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_relatorios_bilstmcrf.pickle',
        'model_file_path': 'out/model_kp_relatorios_bilstmcrf.bin',
        'max_word_size': 68
    }
    execution_lines.append(execution_line)

    ######### KP Segunda Instancia ###############
    # Model 7
    execution_line = {
        'char_embedding_num_units_first_layer': None,
        'char_embedding_num_units_second_layer': None,
        'char_embedding_dimension': None,
        'num_units_first_layer': 64,
        'num_units_second_layer': 128,
        'use_crf': True,
        'num_epochs': 17,
        'dataset_directory': 'data/kp_segunda_instancia/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_segunda_instancia_bilstmcrf.pickle',
        'use_char_embedding': False,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_segunda_instancia_bilstmcrf.pickle',
        'model_file_path': 'out/model_kp_segunda_instancia_bilstmcrf.bin',
        'max_word_size': 52
    }
    execution_lines.append(execution_line)

    ######### BILSTM-CRF best models end ##############


    ######### BILSTM best models beginning ##############

    ######### KP Primeira Instancia ###############
    # Model 8
    execution_line = {
        'char_embedding_num_units_first_layer': None,
        'char_embedding_num_units_second_layer': None,
        'char_embedding_dimension': None,
        'num_units_first_layer': 64,
        'num_units_second_layer': 128,
        'use_crf': False,
        'num_epochs': 4,
        'dataset_directory': 'data/kp_primeira_instancia/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_primeira_instancia_bilstm.pickle',
        'use_char_embedding': False,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_primeira_instancia_bilstm.pickle',
        'model_file_path': 'out/model_kp_primeira_instancia_bilstm.bin',
        'max_word_size': 62
    }
    execution_lines.append(execution_line)

    ######### KP Relatorios ###############
    # Model 4
    execution_line = {
        'char_embedding_num_units_first_layer': None,
        'char_embedding_num_units_second_layer': None,
        'char_embedding_dimension': None,
        'num_units_first_layer': 128,
        'num_units_second_layer': 64,
        'use_crf': False,
        'num_epochs': 3,
        'dataset_directory': 'data/kp_relatorios/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_relatorios_bilstm.pickle',
        'use_char_embedding': False,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_relatorios_bilstm.pickle',
        'model_file_path': 'out/model_kp_relatorios_bilstm.bin',
        'max_word_size': 68
    }
    execution_lines.append(execution_line)

    ######### KP Segunda Instancia ###############
    # Model 20
    execution_line = {
        'char_embedding_num_units_first_layer': None,
        'char_embedding_num_units_second_layer': None,
        'char_embedding_dimension': None,
        'num_units_first_layer': None,
        'num_units_second_layer': 128,
        'use_crf': False,
        'num_epochs': 6,
        'dataset_directory': 'data/kp_segunda_instancia/training/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_segunda_instancia_bilstm.pickle',
        'use_char_embedding': False,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_segunda_instancia_bilstm.pickle',
        'model_file_path': 'out/model_kp_segunda_instancia_bilstm.bin',
        'max_word_size': 52
    }
    execution_lines.append(execution_line)

    ######### BILSTM best models end ##############


    for execution_line in execution_lines:
        char_embedding_num_units_first_layer = execution_line['char_embedding_num_units_first_layer']
        char_embedding_num_units_second_layer = execution_line['char_embedding_num_units_second_layer']
        char_embedding_dimension = execution_line['char_embedding_dimension']
        num_units_first_layer = execution_line['num_units_first_layer']
        num_units_second_layer = execution_line['num_units_second_layer']
        use_crf = execution_line['use_crf']
        dataset_directory = execution_line['dataset_directory']
        tag_vocabulary_file_path = execution_line['tag_vocabulary_file_path']
        use_char_embedding = execution_line['use_char_embedding']
        char_vocabulary_file_path = execution_line['char_vocabulary_file_path']
        model_file_path = execution_line['model_file_path']
        num_epochs = execution_line['num_epochs']
        max_word_size = execution_line['max_word_size']

        if isfile(model_file_path):
            print('#########################################')
            print('### Skipping training of model')
            print('Model file exists at "%s"' % model_file_path)
        else:
            print('#########################################')
            print('### Training of model')
            print('Dataset directory: "%s"' % dataset_directory)
            print('Tag vocabulary file: "%s"' % tag_vocabulary_file_path)
            print('Use char embedding: "%s"' % use_char_embedding)
            print('Char vocabulary file: "%s"' % char_vocabulary_file_path)
            print('Model file: "%s"' % model_file_path)
            print('Number of epochs: %d' % num_epochs)
            print('Maximum word size: %d' % max_word_size)

            train(dataset_directory=dataset_directory, word_embedding_file_path=word_embedding_file_path,
                  model_file_path=model_file_path, tag_vocabulary_file_path=tag_vocabulary_file_path,
                  char_vocabulary_file_path=char_vocabulary_file_path, use_char_embedding=use_char_embedding,
                  num_units_first_layer=num_units_first_layer, num_units_second_layer=num_units_second_layer,
                  char_embedding_num_units_first_layer=char_embedding_num_units_first_layer,
                  char_embedding_num_units_second_layer=char_embedding_num_units_second_layer,
                  char_embedding_dimension=char_embedding_dimension,
                  use_crf=use_crf, max_word_size=max_word_size, batch_size=batch_size, num_epochs=num_epochs,
                  loss=loss, learning_rate=learning_rate, dropout_rate=dropout_rate, verbose=verbose)

