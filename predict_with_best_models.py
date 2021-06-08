# -*- coding: utf-8 -*-

from main import predict


### Configures Tensorflow not allocate the whole memory initially - Beginning
import tensorflow as tf
from keras import backend as k

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
k.tensorflow_backend.set_session(tf.compat.v1.Session(config=config))
### Configures Tensorflow not allocate the whole memory initially - End


if __name__ == "__main__":
    word_embedding_file_path = 'data/best_word_embedding/word2vec_skipgram_s100.txt'

    execution_lines = []

    ######### BILSTM-CRF best models beginning ##############

    ######### KP Primeira Instancia ###############
    execution_line = {
        'dataset_directory': 'data/kp_primeira_instancia/test/',
        'output_directory': 'out/predictions_kp_primeira_instancia/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_primeira_instancia_bilstmcrf.pickle',
        'use_char_embedding': False,
        'max_word_size': 62,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_primeira_instancia_bilstmcrf.pickle',
        'model_file_path': 'out/model_kp_primeira_instancia_bilstmcrf.bin',
    }
    execution_lines.append(execution_line)

    ######### KP Relatorios ###############
    execution_line = {
        'dataset_directory': 'data/kp_relatorios/test/',
        'output_directory': 'out/predictions_kp_relatorios/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_relatorios_bilstmcecrf.pickle',
        'use_char_embedding': True,
        'max_word_size': 68,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_relatorios_bilstmcecrf.pickle',
        'model_file_path': 'out/model_kp_relatorios_bilstmcecrf.bin',
    }
    execution_lines.append(execution_line)

    ######### KP Segunda Instancia ###############
    execution_line = {
        'dataset_directory': 'data/kp_segunda_instancia/test/',
        'output_directory': 'out/predictions_kp_segunda_instancia/',
        'tag_vocabulary_file_path': 'data/tag_vocabulary/kp_segunda_instancia_bilstmcrf.pickle',
        'use_char_embedding': False,
        'max_word_size': 52,
        'char_vocabulary_file_path': 'data/char_vocabulary/kp_segunda_instancia_bilstmcrf.pickle',
        'model_file_path': 'out/model_kp_segunda_instancia_bilstmcrf.bin',
    }
    execution_lines.append(execution_line)

    ######### BILSTM-CRF best models end ##############

    for execution_line in execution_lines:
        dataset_directory = execution_line['dataset_directory']
        output_directory = execution_line['output_directory']
        tag_vocabulary_file_path = execution_line['tag_vocabulary_file_path']
        use_char_embedding = execution_line['use_char_embedding']
        char_vocabulary_file_path = execution_line['char_vocabulary_file_path']
        model_file_path = execution_line['model_file_path']
        max_word_size = execution_line['max_word_size']

        print('#########################################')
        print('### Model predictions')
        print('Dataset directory: "%s"' % dataset_directory)
        print('Output directory: "%s"' % output_directory)
        print('Tag vocabulary file: "%s"' % tag_vocabulary_file_path)
        print('Use char embedding: "%s"' % use_char_embedding)
        print('Maximum word size: %d' % max_word_size)
        print('Char vocabulary file: "%s"' % char_vocabulary_file_path)
        print('Model file: "%s"' % model_file_path)

        predict(dataset_directory=dataset_directory, predictions_directory=output_directory,
                word_embedding_file_path=word_embedding_file_path, model_file_path=model_file_path,
                tag_vocabulary_file_path=tag_vocabulary_file_path, char_vocabulary_file_path=char_vocabulary_file_path,
                use_char_embedding=use_char_embedding, max_word_size=max_word_size)
