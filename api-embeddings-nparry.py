import pandas as pd
import numpy as np

df = pd.read_csv('./output/embedded_1k_reviews.csv')

print(df.ada_embedding.apply(eval))
print(df.ada_embedding)

df['ada_embedding'] = df.ada_embedding.apply(eval).apply(np.array)

print(df.ada_embedding)