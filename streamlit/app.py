import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def local_css(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    assert path.endswith("csv"), "Error: expecting a CSV file!"
    df = pd.read_csv(path)
    df["content_type"] = df["full_id"].apply(
        lambda row: np.where(row.startswith("t1_"), "Comment", "Post")
    )
    return df


@st.cache_data
def load_topics(path: str) -> dict:
    assert path.endswith('json'), 'Error: expecting a JSON file!'
    with open(path, 'r') as f:
        topics = json.load(f)
        topics = {int(k):v for k,v in topics.items()}
        topics = {k: ",".join(v[:5]) for k,v in topics.items()}
    
    return topics


def print_results(df: pd.DataFrame) -> None:
    for i,row in df.iterrows(): 
        cats = []
        for col in df.columns[8:]:
            if row[col] == 1:
                cats.append(col)
        cats = "; ".join(cats)             
        st.markdown(f'**Score:** `{row.score}` **Date:** `{row.month_year}` **ID:** `{row.doccano_id}` **Unique ID:** `{row.unique_id}`')
        st.markdown(f"**Author:** `{row.author}` **Thread Link:** [click here]({row.url}).", unsafe_allow_html=True)
        st.markdown(f'**Labels:** `{cats}`')
        st.markdown(f'**Topic ID:** `{row.topic}` **Topic Words:** `{topics[row.topic]}`')
        st.markdown(f'{row.text}')
        st.markdown('---')


# config
st.set_page_config(
    page_title="IDW Paper Analysis App",
    page_icon="📊"
)

local_css("css/style.css")

# vars
DATA = "idw_reddit_posts.csv"
TOPIC_LIST = "topics.json"

st.title("IDW Paper Analysis App")
st.markdown('---')

df = load_data(os.path.join("..", "data", "coding", "analysis_sample", DATA))
topics = load_topics(os.path.join('data', TOPIC_LIST))

st.markdown("### Data Preview")
st.dataframe(df)
st.markdown("---")

# filters:
obs_type = [
    "Contrarianism",
    "Anti-Contrarianism",
    "Neutral"
]

categories = df.columns[11:]
categories = [i for i in categories if i not in obs_type]

content_type = ["Comment", "Post"]

resp_order = [
    "Highest Score",
    "Lowest Score"
]

with st.form(key="main-filter"):
    # components:
    obs_filter = st.selectbox(
        label="Choose Observation Sentiment",
        options=obs_type
    )

    include_categories = st.multiselect(
        label="Include Categories",
        options=categories,
        key="includes"
    )
    
    exclude_categories = st.multiselect(
        label="Exclude Categories",
        options=categories,
        key="excludes"
    )
    
    content_selector = st.radio(
        label="Choose Content Type",
        options=content_type,
        key="content-type"
    )
    
    result_order = st.radio(
        label="Choose a Sort Option",
        options=resp_order,
    )
    
    submit = st.form_submit_button("Submit")
    
    if submit:
        if len(categories) == 0:
            st.error("Error: you must select at least one category!")
        else:
            st.markdown('---')
            st.markdown('### Results')
            with st.expander(label='Examples', expanded=True):
                script = """<div class='ExampleScroll'></div>"""
                st.markdown(script, unsafe_allow_html=True)
                
                if obs_filter == "Neutral":
                    df_slice = df.loc[(df["Contrarianism"]==0) & (df["Anti-Contrarianism"]==0)]
                else:
                    df_slice = df.loc[df[obs_filter]==1]
                    
                df_slice = df_slice.loc[df_slice[include_categories].eq(1).all(axis=1)]
                df_slice = df_slice.loc[df_slice["content_type"] == content_selector]
                
                if exclude_categories:
                    if any([i in exclude_categories for i in include_categories]):
                        st.error("Error: cannot have overlapping categories!")
                    else:
                        df_slice = df_slice.loc[df_slice[exclude_categories].eq(0).all(axis=1)]
                if result_order == "Highest Score":
                    df_slice.sort_values('score', ascending=False, inplace=True)
                    print_results(df_slice)
                elif result_order == "Lowest Score":
                    df_slice.sort_values("score", ascending=True, inplace=True)
                    print_results(df_slice)
