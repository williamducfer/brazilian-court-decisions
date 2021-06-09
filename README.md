# Information Extraction from Brazilian Court decisions

This project contains the files necessary to run a system to extract and visualize information from Brazilian Court decisions.

We have to run the script *architecture_grid_search.py* to perform the experiments to find the best combination of word embedding and neural network architecture, trained and evaluated through cross-validation. Inside the script, *define_model* method establishes candidate architectures to be assessed. The script produces a very detailed output. If we would like to compare the candidate models in a fast way, we have to run the script *generate_qualities_csv_from_crf_grid_search_log_file.sh* . It generates a CSV with model ID, precision, recall, and F-score.

After finding the best word embedding and the best neural network architecture through cross-validation, we have to train the model, using the whole training data. For that, we created *train_best_models.py* script. In that script, we have to specify the architectures to be trained, dataset directories, and where files of models will be stored after training.

After training the model, we have to evaluate it, using the test data. For that, we created *evaluate_best_models.py* script. In that script, we have to specify dataset directories to be evaluated, files of models, and char embedding information about each model.

To generate predictions with a trained model, we have to run *predict_with_best_models.py* script. In that script, we have to specify dataset directories to generate predictions, files of models, char embedding information about each model, and output directories to save the predictions. At the end of the execution, for each prediction directory, we have the same files than in the original directories with an extra column that correspond to predictions, and an additional file called *extracted_annotations.csv*.
