# -*- coding: utf-8 -*-
# Author: Sean Doody
# Email: sdoody1@umd.edu
# Date: May 30, 2023
'''
This script takes a list of full Reddit IDs and gets
the updated scores with PRAW.

The output is written to a JSON file that can be
mapped to the full_id of the post/comment.
'''
import os
import time
import json

import sqlite3
import pandas as pd

import praw
from tqdm import tqdm


def main():
    start = time.time()
    
    # grab data:
    DB = 'idw_reddit.db'
    conn = sqlite3.connect(
        os.path.join(
            'data',
            'sqlite',
            DB
        )
    )

    tables = ['comments', 'posts']

    objects = []
    for table in tables:
        full_ids = pd.read_sql(
            f'SELECT full_id FROM {table}',
            conn
        )['full_id'].tolist()
        objects = full_ids + objects

    conn.close()

    # initiate PRAW:
    with open(os.path.join('credentials', 'praw.json'), 'r') as f:
        credentials = json.load(f)

    reddit = praw.Reddit(
        username=credentials['username'],
        password=credentials['password'],
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret'],
        user_agent=credentials['user_agent']
    )

    # get scores:
    scores = {}
    for obj in tqdm(reddit.info(fullnames=objects)):
        scores[obj.fullname] = obj.score

    with open(os.path.join('data', 'updated_scores', 'score_mapper.json'), 'w') as f:
        json.dump(scores, f, indent=4)
    
    end = time.time()
    runtime = round((end - start) / 60, 3)
    print(f'Finished in {runtime} minutes')


if __name__ == '__main__':
    main()