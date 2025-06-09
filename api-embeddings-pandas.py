import os
import pandas as pd
import numpy as np

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
    project=os.environ.get("OPENAI_PROJECT")
)

def get_embedding(text, model="text-embedding-3-small"):
    """Get the embedding for a given text using OpenAI API."""
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text],model=model, dimensions=256).data[0].embedding


print(os.getcwd())
df = pd.read_csv('./data/Reviews_short.csv')
df = df[["Time","ProductId","UserId","Score","Summary","Text"]]

df = df.dropna()

df["combined"] = ("Title: " + df["Summary"].str.strip() + "; Content: " + df["Text"].str.strip())
df['ada_embedding'] = df.combined.apply(lambda x: get_embedding(x, model="text-embedding-3-small"))

df.to_csv('./output/embedded_1k_reviews_256.csv', index=False)

print(df.head(5))
print(df.combined)

