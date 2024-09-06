import os
import pickle
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
 
def make_embeddings(df: pd.DataFrame, doc_column: str, model: str) -> pd.DataFrame:
    embedding_model = SentenceTransformer(model)
    embeddings = embedding_model.encode(df[doc_column].tolist(), show_progress_bar=True)
    print("Finished encoding texts!")
    return embeddings


def save_embeddings(embeddings: list, path: str) -> None:
    with open(path, "wb") as pkl:
        pickle.dump(embeddings, pkl)
    print("Finished saving!")
        

def load_embeddings(embeddings_path: str) -> np.array:
    with open(embeddings_path, "rb") as pkl:
        print(f"Loading: {embeddings_path}")
        embeddings = pickle.load(pkl)
    
    print(f"Done loading!")
    return embeddings