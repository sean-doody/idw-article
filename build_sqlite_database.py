# -*- coding: utf-8 -*-
# Author: Sean Doody
# Email: sdoody1@umd.edu
# Date: May 1, 2023
'''
This script loads the compressed ZST acrhives of Reddit comments and posts
and writes them to separate tables in a SQLite database.
'''
import os
from utils.zst2frame.zst2frame import ZST2Frame

def main():
    reddit_zst_files = {
        'comments': 'IntellectualDarkWeb_comments.zst',
        'posts': 'IntellectualDarkWeb_submissions.zst'
    }

    for file in reddit_zst_files:
        data = ZST2Frame(os.path.join('data', 'raw', reddit_zst_files[file]))
        data.make_pandas_dataframe()
        data.save_to_sqlite()


if __name__ == '__main__':
    main()