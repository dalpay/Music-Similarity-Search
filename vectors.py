import numpy as np


def compute_vector(features, mode='gauss'):

    vector = []

    if (mode == 'gauss'):
        vector = gauss_vector(features)
    elif (mode == 'gmm'):
        vector = gmm_vector(features)
    elif (mode == 'pca'):
        vector = pca_vector(features)

    if vector:
        return vector.tolist()
    else:
        return None

def gauss_vector(features):
    
    mean = np.mean(features, axis=0)
    covar = np.cov(features, rowvar=False)
    vec = mean

    for k in range(len(mean)):

        diag = np.diag(covar, k)
        vec = np.concatenate((vec, diag))

    return vec

def gmm_vector(features):

    return None

def pca_vector(features):

    return None
