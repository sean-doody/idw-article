# Read Me

This is the code used for the article, "Making Sense of a Pandemic: Reasoning About COVID-19 in the Intellectual Dark Web".

**IMPORTANT:** to run the analysis contained herein, you must have access to the [Pushshift Reddit dumps](https://arxiv.org/abs/2001.08435), both posts and comments, from 2018 through 2022. Given Reddit's updated API terms, the raw data is not included in this repository, and must be built from source.

The relevant conda environemnt  can be built by running:

```bash
conda env create -n idw-article --file environment.yml
```

## To build the datasets:

1. First, run `combine_folder_multiprocess.py` to extract the relevant Pushshift Reddit data (note: you must modify the shell scripts in the `reddit-scripts` folder to match your file system). This script was written by [Watchful1](https://github.com/Watchful1/PushshiftDumps).
2. Then, run `build_sqlite_database.py` to extract the Pushshift data form the ZST files and store them in a SQLite database. Two tables will be created: `comments` and `posts`.
3. Finally, run `build_training_corpus.py` to process the text and prepare the training corpus for topic modeling.

## To train the topic model:

Consult the Jupyter Notebooks in the `notebooks` subfolder. They are labeled sequentially. **NOTE:** the topic model was trained on [Paperspace Gradient](https://www.paperspace.com/gradient/notebooks) CUDA notebook instances.
