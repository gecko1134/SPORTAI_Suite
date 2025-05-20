import pandas as pd
from scipy.stats import ttest_ind

def optimize_campaign(invites: pd.DataFrame) -> dict:
    groupA = invites[invites['variant'] == 'A']['response_rate']
    groupB = invites[invites['variant'] == 'B']['response_rate']
    stat, p = ttest_ind(groupA, groupB)
    winner = 'A' if groupA.mean() > groupB.mean() else 'B'
    return {'winner': winner, 'p_value': p}
