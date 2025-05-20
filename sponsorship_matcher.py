import pandas as pd

def match_sponsors(assets: pd.DataFrame, sponsors: pd.DataFrame) -> pd.DataFrame:
    assets['key'] = 1
    sponsors['key'] = 1
    matrix = assets.merge(sponsors, on='key').drop('key', axis=1)
    matrix['score'] = matrix['expected_exposure'] * matrix['sponsor_budget'] / matrix['asset_cost']
    best = (matrix.sort_values('score', ascending=False)
                  .groupby('sponsor_id', as_index=False)
                  .first())
    return best[['sponsor_id', 'asset_id', 'score']]
