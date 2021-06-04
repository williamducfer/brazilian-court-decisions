# -*- coding: utf-8 -*-

import nltk
import sklearn_crfsuite
import numpy as np
import os
from sklearn.model_selection import KFold
import argparse
import conlleval

random_state_seed = 444
num_folds = 5


# Methods for features extraction
def generate_features(word, pos, feature_prefix):
    word_lower = word.lower()
    features = {
        feature_prefix + 'word.lower()': word_lower,
        feature_prefix + 'word[-4:]': word_lower[-4:],
        feature_prefix + 'word[-3:]': word_lower[-3:],
        feature_prefix + 'word[:-4]': word_lower[:-4],
        feature_prefix + 'word[:-3]': word_lower[:-3],
        feature_prefix + 'word[:3]': word_lower[:3],
        feature_prefix + 'word.isupper()': word.isupper(),
        feature_prefix + 'word.istitle()': word.istitle(),
        feature_prefix + 'word.isdigit()': word.isdigit(),
        feature_prefix + 'postag': pos
    }
    
    return features


def word2features(sent, i):
    word_idx = 0
    pos_idx = 1
    
    word = sent[i][word_idx]
    pos = sent[i][pos_idx]
    
    features = {
        #'bias': 1.0,
    }
    
    window = 5
    
    for relative_position in range(-window, window + 1):
        position = i + relative_position
        if position >= 0 and position < len(sent):
            word = sent[position][word_idx]
            pos = sent[position][pos_idx]
            
            feature_prefix = '%d:' % relative_position
            
            features.update(generate_features(word, pos, feature_prefix))
    
    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, pos, label in sent]

def sent2tokens(sent):
    return [token for token, pos, label in sent]


def grid_search(dataset_dir):
    # Runs a grid search through c1 and c2 candidate values
    c1_list = [0.1, 0.01, 0.001]
    c2_list = [0.1, 0.01, 0.001]

    for c1 in c1_list:
        for c2 in c2_list:
            print('############################################')
            print('For c1 = %f and c2 = %f' % (c1, c2))

            train_cv(dataset_dir, c1, c2)
            print('\n\n')


def train_cv(dataset_dir, c1, c2):
    training_dir = "%s/training" % dataset_dir

    # Reads data using CoNLLCorpusReader
    cross_validation_corpus = nltk.corpus.reader.conll.ConllCorpusReader(training_dir, '.*.txt', ['words', 'pos', 'chunk'])

    cross_validation_sents = list(cross_validation_corpus.iob_sents())

    kfold = KFold(n_splits=num_folds, shuffle=True, random_state=random_state_seed)

    num_cross_validation_samples = len(cross_validation_sents)
    cross_validation_sents = np.array(cross_validation_sents)

    i = 0
    cv_score_dict = {'precision': [], 'recall': [], 'f1': []}

    for training_indexes, validation_indexes in kfold.split(np.zeros(num_cross_validation_samples)):
        training_dataset_X = [sent2features(s) for s in cross_validation_sents[training_indexes]]
        training_dataset_y = [sent2labels(s) for s in cross_validation_sents[training_indexes]]

        validation_dataset_X = [sent2features(s) for s in cross_validation_sents[validation_indexes]]
        validation_dataset_y = [sent2labels(s) for s in cross_validation_sents[validation_indexes]]

        print('============================================')
        print('Running fold %d of %d...' % (i + 1, num_folds))

        crf = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=c1,
            c2=c2,
            max_iterations=100,
            all_possible_transitions=True
        )
        crf.fit(training_dataset_X, training_dataset_y)

        validation_dataset_y_pred = crf.predict(validation_dataset_X)

        validation_dataset_y_flat_upper = [item.upper() for sublist in validation_dataset_y for item in sublist]
        validation_dataset_y_pred_flat_upper = [item.upper() for sublist in validation_dataset_y_pred for item in sublist]

        conll_dict = conlleval.evaluate(validation_dataset_y_flat_upper, validation_dataset_y_pred_flat_upper, verbose=False)

        cv_score_dict['precision'].append(conll_dict[0])
        cv_score_dict['recall'].append(conll_dict[1])
        cv_score_dict['f1'].append(conll_dict[2])

        print('============================================')
        print('Fold %d quality: precision = %f, recall = %f, f1 = %f' % (i + 1, conll_dict[0], conll_dict[1], conll_dict[2]))

        i += 1

    print('============================================')
    print('Mean quality of cross-validation: precision = %f, recall = %f, f1 = %f' % (np.mean(cv_score_dict['precision']), np.mean(cv_score_dict['recall']), np.mean(cv_score_dict['f1'])))


def evaluate(dataset_dir, c1, c2):
    training_dir = "%s/training" % dataset_dir
    test_dir = "%s/test" % dataset_dir

    assert c1 is not None
    assert c2 is not None

    print('Running evaluation of documents in dataset "%s" using c1 = "%f" and c2 = "%f"...' % (test_dir, c1, c2))

    # Reads data using CoNLLCorpusReader
    cross_validation_corpus = nltk.corpus.reader.conll.ConllCorpusReader(training_dir, '.*.txt', ['words', 'pos', 'chunk'])
    test_corpus = nltk.corpus.reader.conll.ConllCorpusReader(test_dir, '.*.txt', ['words', 'pos', 'chunk'])

    cross_validation_sents = list(cross_validation_corpus.iob_sents())
    test_sents = list(test_corpus.iob_sents())

    training_sents = np.array(cross_validation_sents)
    test_sents = np.array(test_sents)

    training_dataset_X = [sent2features(s) for s in training_sents]
    training_dataset_y = [sent2labels(s) for s in training_sents]

    test_dataset_X = [sent2features(s) for s in test_sents]
    test_dataset_y = [sent2labels(s) for s in test_sents]

    crf = sklearn_crfsuite.CRF(
            algorithm='lbfgs',
            c1=c1,
            c2=c2,
            max_iterations=100,
            all_possible_transitions=True
        )
    crf.fit(training_dataset_X, training_dataset_y)

    test_dataset_y_pred = crf.predict(test_dataset_X)

    test_dataset_y_flat_upper = [item.upper() for sublist in test_dataset_y for item in sublist]
    test_dataset_y_pred_flat_upper = [item.upper() for sublist in test_dataset_y_pred for item in sublist]

    conll_dict = conlleval.evaluate(test_dataset_y_flat_upper, test_dataset_y_pred_flat_upper, verbose=True)

    print('============================================')
    print('Evaluation on test set: precision = %f, recall = %f, f1 = %f' % (conll_dict[0], conll_dict[1], conll_dict[2]))


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()

    args_parser.add_argument('action', choices=['grid_search', 'evaluate'], help='Specifies whether grid_search or evaluate.')
    args_parser.add_argument('dataset_dir', help='Dataset directory to perform a specified action.')
    args_parser.add_argument('-c1', '--c1_value', type=float, help='Value for parameter c1. Used for action evaluate.')
    args_parser.add_argument('-c2', '--c2_value', type=float , help='Value for parameter c2. Used for action evaluate.')

    args = args_parser.parse_args()

    dataset_directory = args.dataset_dir

    if args.action == 'grid_search':
        grid_search(dataset_directory)
    elif args.action == 'evaluate':
        c1_value = args.c1_value
        c2_value = args.c2_value

        evaluate(dataset_directory, c1_value, c2_value)
