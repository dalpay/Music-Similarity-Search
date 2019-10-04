import numpy as np


def vector_processor(method='gauss'):
    '''
    Returns the function to compute the embedding vector for a given method.
    Since Spark UDF does not accept keyword arguments, the method keyword 
    argument is seperated from the function that computes the vector by placing 
    it within this function.
    '''

    def compute_vector(*features):

        vector = []

        for feature in features:

            if (method.lower() == 'gauss'):
                vec = gauss_vector(feature)
            elif (method.lower() == 'gmm'):
                vec = gmm_vector(feature)
            elif (method.lower() == 'pca'):
                vec = pca_vector(feature)

            if (vec is not None):
                vector += vec.tolist()

        if vector:
            return vector
        else:
            return None

    return compute_vector

def gauss_vector(features):
    '''
    Computes a vector containing the mean and the upper triangle of the 
    covariance matrix of the features.
    '''

    mean = np.mean(features, axis=0)
    covar = np.cov(features, rowvar=False)
    vec = mean

    for k in range(len(mean)):

        diag = np.diag(covar, k)
        vec = np.concatenate((vec, diag))

    return vec

def gmm_vector(features):
    '''
    Not yet supported.
    Computes a vector containing the means of the GMM clusters of the features.
    '''

    return None

def pca_vector(features):
    '''
    Not yet supported.
    Computes a vector containing the PCA reduced features.
    '''

    return None
