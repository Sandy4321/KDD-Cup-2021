
import gc
import pandas as pd
import numpy as np
import sys
import warnings

from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD, NMF

from utils import save2pkl, loadpkl, line_notify

warnings.filterwarnings('ignore')

#==============================================================================
# Preprocessing Profiles
#==============================================================================

def main(num_rows=None):
    # load csv & pkl
    profiles = pd.read_csv('../input/data_set_phase2/profiles.csv')

    # change columns name
    profiles.columns = ['pid']+['profile_{}'.format(i) for i in range(0,66)]

    # feature engineering
    feats = [f for f in profiles.columns.to_list() if f not in ['pid']]

    profiles['profile_sum'] = profiles[feats].mean(axis=1)
    profiles['profile_mean'] = profiles[feats].sum(axis=1)
    profiles['profile_std'] = profiles[feats].std(axis=1)

    profiles['profile_sum_count'] = profiles['profile_sum'].map(profiles['profile_sum'].value_counts())

    # svd features
    svd = TruncatedSVD(n_components=20, n_iter=20, random_state=326)
    svd_x = svd.fit_transform(profiles[feats].values)
    svd_x = pd.DataFrame(svd_x)
    svd_x.columns = ['profile_svd_{}'.format(i) for i in range(20)]
    svd_x['pid'] = profiles['pid']

    # merge
    profiles = profiles.merge(svd_x, on='pid', how='left')

    # NMF features
    nmf = NMF(n_components=20, init='random', random_state=326)
    nmf_x = nmf.fit_transform(profiles[feats].values)
    nmf_x = pd.DataFrame(nmf_x)
    nmf_x.columns = ['profile_nmf_{}'.format(i) for i in range(20)]
    nmf_x['pid'] = profiles['pid']

    # merge
    profiles = profiles.merge(nmf_x, on='pid', how='left')

    # k-means clustering
    kmeans_model = KMeans(n_clusters=10, random_state=326)
    kmeans_model.fit(profiles[feats].values)
    profiles['profile_k_means'] = kmeans_model.labels_

    # save as pkl
    save2pkl('../features/profiles.pkl', profiles)

    line_notify('{} finished.'.format(sys.argv[0]))

if __name__ == '__main__':
    main()
