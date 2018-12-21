import numpy as np
import pandas as pd


dfs = []
for y in range(2000, 2014):
    df1 = pd.DataFrame(np.random.randn(10))
    df1['year'] = y
    df1['origin'] = 'df1'

    df2 = pd.DataFrame(np.random.randn(10))
    df2['year'] = y
    df2['origin'] = 'df2'

    df3 = pd.DataFrame(np.random.randn(10))
    df3['year'] = y
    df3['origin'] = 'df3'

    dfs.extend([df1, df2, df3])

df = pd.concat(dfs)
df = df.set_index(['year'])
print(df)