# -*- coding: utf-8 -*-
# Author: Sean Doody
# Email: sdoody1@umd.edu
# Date: May 1, 2023

import os
import io
import json
import pandas as pd
from tqdm import tqdm
import zstandard as zstd
import sqlite3
from sqlite3 import Error

class ZST2Frame:
    def __init__(self, zst_path: str):
        self.zst_path = zst_path

        if self.zst_path.endswith('comments.zst'):
            self.path_type = 'comments'
        elif self.zst_path.endswith('submissions.zst'):
            self.path_type = 'posts'
        else:
            raise Exception('Unknown Pushshift file type: check raw data!')
        
        # for making and writing to SQLite database
        self.sqlite_db_name = 'idw_reddit.db'
        
    def make_pandas_dataframe(self):
        print(f'Iterating over {self.zst_path}')
        new_line_json = []
        with open(self.zst_path, 'rb') as reddit_data:
            DCTX = zstd.ZstdDecompressor(max_window_size=2**31)
            stream_reader = DCTX.stream_reader(reddit_data)
            text_stream = io.TextIOWrapper(stream_reader, encoding='utf-8')
            for line in tqdm(text_stream):
                new_line_json.append(json.loads(line))
        
        if self.path_type == 'comments':
            fields = [
                'id',
                'link_id',
                'parent_id',
                'permalink',
                'subreddit',
                'subreddit_id',
                'created_utc',
                'retrieved_utc',
                'author',
                'distinguished',
                'body',
                'score',
                'score_hidden',
                'total_awards_received',
            ]
        
        if self.path_type == 'posts':
            fields= [
                'id',
                'permalink',
                'url',
                'domain',
                'created_utc',
                'retrieved_utc',
                'subreddit',
                'subreddit_id',
                'author',
                'distinguished',
                'title',
                'selftext',
                'score',
                'stickied',
                'total_awards_received',
                'num_comments',
                'num_crossposts',
                'view_count'  
            ]

        print(f'Porting {len(new_line_json)} new-line JSON {self.path_type} to Pandas')
        df = pd.DataFrame(new_line_json)
        self.df = df[fields].copy()
                
        print('Making string date column')
        self.df['date'] = pd.to_datetime(self.df['created_utc'], unit='s').dt.strftime('%Y-%m-%d')
        
        # add full ID:
        if self.path_type == 'comments':
            self.df['full_id'] = 't1_' + self.df['id']
            
        if self.path_type == 'posts':
            self.df['full_id'] = 't3_' + self.df['id']
        
        # add anonymous unique ID:
        if self.path_type == 'comments':
            prefix = 'C'
            idx_range = [i+1 for i in range(len(self.df))]
            assert len(idx_range) == len(self.df)
            idx_range = [f'{prefix}{str(i).zfill(2)}' for i in idx_range]
            self.df['unique_id'] = idx_range
            assert len(self.df['unique_id'].unique()) == len(self.df)
        
        if self.path_type == 'posts':
            prefix = 'P'
            idx_range = [i+1 for i in range(len(self.df))]
            assert len(idx_range) == len(self.df)
            idx_range = [f'{prefix}{str(i).zfill(2)}' for i in idx_range]
            self.df['unique_id'] = idx_range
            assert len(self.df['unique_id'].unique()) == len(self.df)
            
        print('Done!')
    
    
    def save_to_sqlite(self):
        assert self.df is not None, 'No dataframe!'

        SQLITE_PATH = os.path.join('data', 'sqlite', self.sqlite_db_name)
        if not os.path.exists(SQLITE_PATH):
            self.create_sqlite_database()
        
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            
            print(f'Saving {len(self.df)} {self.path_type}')
            self.df.to_sql(
                name=self.path_type,
                con=conn,
                if_exists='replace'
            )
        except Error as sqlite_error:
            print(sqlite_error)
        finally:
            if conn:
                print('Done!')
                conn.close()

    def create_sqlite_database(self):
        SQLITE_DB_NAME = self.sqlite_db_name
        SQLITE_PATH = os.path.join('data', 'sqlite', SQLITE_DB_NAME)

        conn = None
        try:
            conn = sqlite3.connect(SQLITE_PATH)
            print(f'Created new SQLite database: {SQLITE_PATH}')
            print(f'SQLite Version: {sqlite3.version}')
        except Error as sqlite_error:
            print(f'{sqlite_error}')
        finally:
            if conn:
                conn.close()