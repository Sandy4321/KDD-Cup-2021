
import datetime
import feather
import gc
import json
import pandas as pd
import numpy as np
import warnings

from utils import loadpkl, to_feature, to_json, removeCorrelatedVariables, removeMissingVariables

warnings.filterwarnings('ignore')

#==============================================================================
# Aggregation
#==============================================================================

def main(num_rows=None):
    # load pkls
    df = loadpkl('../features/plans.pkl')
    queries = loadpkl('../features/queries.pkl')
    profiles = loadpkl('../features/profiles.pkl')
    queries_pred = loadpkl('../features/queries_pred.pkl')

    # merge
    df = pd.merge(df, queries, on=['sid','click_mode'], how='left')
    df = pd.merge(df, profiles, on='pid', how='left')
    df = pd.merge(df, queries_pred, on='sid', how='left')

    del queries, profiles, queries_pred
    gc.collect()

    # count features
    df['pid_count'] = df['pid'].map(df['pid'].value_counts())

    # time diff
    df['plan_req_time_diff'] = (df['plan_time']-df['req_time']).astype(int)

    # distance ratio
    cols_plan_distance = ['plan_{}_distance'.format(i) for i in range(0,7)]

    for i, c in enumerate(cols_plan_distance):
        df['plan_queries_distance_ratio{}'.format(i)] = df[c] / df['queries_distance']

    # remove missing variables
    col_missing = removeMissingVariables(df,0.75)
    df.drop(col_missing, axis=1, inplace=True)

    # remove correlated variables
    col_drop = removeCorrelatedVariables(df,0.95)
    df.drop(col_drop, axis=1, inplace=True)

    # save as feather
    to_feature(df, '../features')

    # save feature name list
    features_json = {'features':df.columns.tolist()}
    to_json(features_json,'../features/000_all_features.json')

if __name__ == '__main__':
    main()
