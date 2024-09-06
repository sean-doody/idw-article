import json
import sqlite3
import pandas as pd
from tqdm import tqdm
tqdm.pandas()

def load_embeddings(text_embedding_data: str, chunksize: int=5000) -> pd.DataFrame:
    embeds = pd.DataFrame()

    read_lines = 0
    for chunk in tqdm(pd.read_json(text_embedding_data, lines=True, chunksize=chunksize)):
        embeds = pd.concat([embeds, chunk])
        read_lines += len(chunk)
        del chunk
        
    embeds.sort_values("full_id", inplace=True)
    return embeds


def load_and_prep_data(data: str, sql_db: str, topic_group_file: str, score_file: str) -> pd.DataFrame:
    df = pd.read_csv(data)

    # grab SQL data:
    conn = sqlite3.connect(sql_db)
    tables = ["comments", "posts"]

    sql_frame = pd.DataFrame()
    for table in tables:
        temp = pd.read_sql(
            f"SELECT full_id, unique_id, author, created_utc, permalink FROM {table}",
            conn
        )
        sql_frame = pd.concat([sql_frame, temp])
    conn.close()

    # add ates, topic groups, and updated scores:
    print("Formatting dates")
    sql_frame["date"] = pd.to_datetime(sql_frame["created_utc"], unit="s").dt.date

    date_mapper = dict(
        zip(
            sql_frame["full_id"],
            sql_frame["date"]
        )
    )

    print("Getting topic groups")
    with open(topic_group_file, "r") as f:
        topic_groups = json.load(f)

    topic_groups = {int(k):v for k,v in topic_groups.items()}

    print("Getting updated scores")
    with open(score_file, "r") as f:
        score_mapper = json.load(f)

    # map to dataframe:
    print("Mapping updated data to dataframe...")
    df["date"] = df["full_id"].map(date_mapper)
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df["month"] = pd.to_datetime(df["date"]).dt.month
    df["month_year"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")
    df["quarter"] = pd.to_datetime(df["date"]).dt.to_period("Q")

    df["permalink"] = df["full_id"].map(
        dict(
            zip(
                sql_frame["full_id"],
                sql_frame["permalink"]
            )
        )
    )

    df["author"] = df["full_id"].map(
        dict(
            zip(
                sql_frame.full_id,
                sql_frame.author
            )
        )
    )

    df["topic_group"] = df["new_topic"].map(topic_groups)
    df["score"] = df["full_id"].map(score_mapper)
    df["unique_id"] = df["full_id"].map(dict(zip(sql_frame.full_id, sql_frame.unique_id)))
    print("Done")

    return df