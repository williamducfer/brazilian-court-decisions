from keras.models import load_model as keras_load_model
from keras.models import save_model as keras_save_model
from keras_contrib.layers import CRF
from keras_contrib.losses import crf_loss
from keras.callbacks import ModelCheckpoint, EarlyStopping
import numpy as np
from sklearn.model_selection import KFold
import conlleval
from collections import OrderedDict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


class Tagger():

    def __init__(self, dataset=None, model=None):
        self.dataset = dataset
        self.model = model


    def set_dataset(self, dataset):
        self.dataset = dataset


    def set_model(self, model):
        self.model = model


    def save_model(self, model_file_path):
        keras_save_model(self.model, model_file_path)


    def _create_custom_objects(self):
        instanceHolder = {"instance": None}

        class ClassWrapper(CRF):
            def __init__(self, *args, **kwargs):
                instanceHolder["instance"] = self
                super(ClassWrapper, self).__init__(*args, **kwargs)

        def loss(*args):
            method = getattr(instanceHolder["instance"], "loss_function")
            return method(*args)

        return {"CRF": ClassWrapper, "loss": loss, "crf_loss": crf_loss}


    def load_model(self, model_file_path):
        self.model = keras_load_model(model_file_path, custom_objects=self._create_custom_objects())


    def train(self, num_epochs, batch_size, verbose=False):
        history = self.model.fit(self.dataset.get_X(), self.dataset.Y, epochs=num_epochs,
                                 batch_size=batch_size, verbose=verbose)


    def train_cv(self, num_epochs, num_folds, batch_size, random_state_seed, plot_file_path_prefix='out/plot_cv_fold',
                 best_model_temp_file_path=".best_model.bin", verbose=False):

        kfold = KFold(n_splits=num_folds, shuffle=True, random_state=random_state_seed)

        num_samples = len(self.dataset.X)

        i = 0
        quality_mean = {'precision': [], 'recall': [], 'f1': []}

        for training_indexes, validation_indexes in kfold.split(np.zeros(num_samples)):
            if self.dataset.use_char_embedding:
                training_X_part1 = self.dataset.X[training_indexes]
                training_X_part2 = self.dataset.X_char[training_indexes]
                training_X = [training_X_part1, training_X_part2]

                validation_X_part1 = self.dataset.X[validation_indexes]
                validation_X_part2 = self.dataset.X_char[validation_indexes]
                validation_X = [validation_X_part1, validation_X_part2]

            else:
                training_X = self.dataset.X[training_indexes]
                validation_X = self.dataset.X[validation_indexes]

            training_Y = self.dataset.Y[training_indexes]

            validation_Y = self.dataset.Y[validation_indexes]
            validation_sentences_sizes = self.dataset.sentences_sizes[validation_indexes]

            print('============================================')
            print('Running fold %d of %d...' % (i + 1, num_folds))

            best_model_check_point = ModelCheckpoint(best_model_temp_file_path, mode='min', monitor='val_loss',
                                                     save_best_only=True, save_weights_only=True)

            early_stopping_check_point = EarlyStopping(mode='min', monitor='val_loss', patience=10)

            history = self.model.fit(training_X, training_Y, validation_data=(validation_X, validation_Y),
                                     epochs=num_epochs, batch_size=batch_size, verbose=verbose,
                                     callbacks=[best_model_check_point, early_stopping_check_point])

            min_validation_loss = np.argmin(history.history['val_loss']) + 1
            print('Epoch that presented the least validation loss: %d' % min_validation_loss)

            plot_file_path = "%s%d.png" % (plot_file_path_prefix, i + 1)
            self._plot(history=history, file_path=plot_file_path)

            self.model.load_weights(best_model_temp_file_path)
            os.remove(best_model_temp_file_path)

            sentences_predicted_classes = self.model.predict(x=validation_X)
            sentences_predicted_indexes = np.argmax(sentences_predicted_classes, axis=-1)

            quality = self._evaluate_locally(validation_Y.reshape(validation_Y.shape[0], validation_Y.shape[1]),
                                             sentences_predicted_indexes, validation_sentences_sizes, verbose)

            quality_mean["precision"].append(quality["precision"])
            quality_mean["recall"].append(quality["recall"])
            quality_mean["f1"].append(quality["f1"])

            print('Fold %d quality:' % (i + 1))
            for metric, value in quality.items():
                print("%s: %.2f percent" % (metric, value))

            i += 1

        print('##############################')
        print('Mean quality of cross-validation: precision = %.2f, recall = %.2f, f1 = %.2f' % (np.mean(quality_mean['precision']),
                                                                                                np.mean(quality_mean['recall']),
                                                                                                np.mean(quality_mean['f1'])))

    def _plot(self, history, file_path):
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title('Model loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='upper right')
        plt.savefig(file_path)
        plt.close()


    def _evaluate_locally(self, true_indexes, predicted_indexes, sentences_sizes, verbose):
        true_tags = []
        predicted_tags = []

        for i in range(len(true_indexes)):
            sentence_true_tags = self.dataset.get_tags_from_indexes(true_indexes[i][:sentences_sizes[i]])
            sentence_predicted_tags = self.dataset.get_tags_from_indexes(predicted_indexes[i][:sentences_sizes[i]])

            assert len(sentence_true_tags) == len(sentence_predicted_tags), "Error: number of true tags is different from " \
                                                                            "the number of predicted tags."

            true_tags.extend(sentence_true_tags)
            predicted_tags.extend(sentence_predicted_tags)

        quality = conlleval.evaluate(true_tags, predicted_tags, verbose=verbose)

        quality_metrics = OrderedDict()

        quality_metrics['precision'] = quality[0]
        quality_metrics['recall'] = quality[1]
        quality_metrics['f1'] = quality[2]

        return quality_metrics


    def evaluate(self, verbose=False):
        sentences_predicted_classes = self.model.predict(x=self.dataset.get_X())
        sentences_predicted_indexes = np.argmax(sentences_predicted_classes, axis=-1)

        quality = self._evaluate_locally(self.dataset.Y.reshape(self.dataset.Y.shape[0], self.dataset.Y.shape[1]),
                                         sentences_predicted_indexes, self.dataset.sentences_sizes, verbose)

        return quality


    def predict(self, predictions_directory):
        sentences_predictions_classes = self.model.predict(x=self.dataset.get_X())
        sentences_predictions_indexes = np.argmax(sentences_predictions_classes, axis=-1)

        self.dataset.set_Y(sentences_predictions_indexes)

        self.dataset.save(predictions_directory)

        self.dataset.save_in_one_single_file(predictions_directory)
