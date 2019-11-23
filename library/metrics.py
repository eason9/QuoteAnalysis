import spacy
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches

from matplotlib import pyplot as plt
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import TreebankWordTokenizer
from numpy.linalg import norm
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer


tokenizer = TreebankWordTokenizer()
eng_stopwords = tuple(stopwords.words("english"))
stemmer = PorterStemmer()
nlp = spacy.load("en_core_web_lg")


def tokenization(sent):
    """
    @author: Mihir Gadgil
    Tokenizer for vectorizing sentences.
    """
    # Tokenize sentence
    tokens = tokenizer.tokenize(sent)
    # Remove stopwords and stemming
    processed_tokens = [stemmer.stem(token) for token in tokens if token not in eng_stopwords]
    return processed_tokens


# Text vectorizer for CosineSimilarity
vectorizer = CountVectorizer(tokenizer=tokenization, binary=True)


def JaccardSimilarity(sent1, sent2):
    """
    @author: Mihir Gadgil
    Sentence Jaccard similarity.
    """
    tokens1 = set(tokenizer.tokenize(sent1))
    tokens2 = set(tokenizer.tokenize(sent2))

    return len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2))


def CosineSimilarity(sent1, sent2):
    """
    @author: Mihir Gadgil
    Sentence cosine similarity.
    """
    sents = vectorizer.fit_transform([sent1, sent2]).toarray()
    return np.matmul(sents[0], sents[1].T) / (norm(sents[0]) * norm(sents[1]))


def QuoteWord2Vec(quote_dict):
    """Returns word embeddings."""
    quote_vecs = []
    for quotes in quote_dict.values():
        for quote in quotes:
            quote_vecs.append(nlp(quote).vector)
    return np.asarray(quote_vecs)


def KMeansClusteringElbowCurve(X):
    """Shows an elbow curve plot to determine the appropriate number of k-means clusters."""
    distorsions = []
    for k in range(1, 7):
        kmeans_model = KMeans(n_clusters=k)
        kmeans_model.fit(X)
        distorsions.append(kmeans_model.inertia_)
    fig = plt.figure(figsize=(15, 5))
    plt.plot(range(1, 7), distorsions)
    plt.title('Elbow Curve')
    plt.show()


def KMeansClustering(X, quote_dict, clusters=6):
    """Returns a k-means model and a pandas data frame containing quote information and cluster label."""
    kmeans_model = KMeans(n_clusters=clusters, random_state=42).fit(X)
    kmeans_labels = kmeans_model.labels_
    kmeans_df = pd.DataFrame(columns=['news_source', 'quote', 'kmeans_label'])
    for quote_key, quote_list in zip(quote_dict.keys(), quote_dict.values()):
        for quote, label in zip(quote_list, kmeans_labels):
            add_dict = {'news_source': quote_key, 'quote': quote, 'kmeans_label': label}
            kmeans_df = kmeans_df.append(add_dict, ignore_index=True)
    return kmeans_model, kmeans_df


def KMeansClusteringPlot(X, kmeans_model, kmeans_df):
    """Show clusters with centroids from k-means model."""
    fig, ax = plt.subplots()
    for i, news in zip(range(len(X)), kmeans_df['news_source'].tolist()):
        if news == 'fox':
            ax.plot(X[i, 0], X[i, 1], c='magenta', marker='o', linestyle='', ms=12, label=news)
        elif news == 'cnn':
            ax.plot(X[i, 0], X[i, 1], c='cyan', marker='o', linestyle='', ms=12, label=news)
        elif news == 'bbc':
            ax.plot(X[i, 0], X[i, 1], c='green', marker='o', linestyle='', ms=12, label=news)
        elif news == 'bb':
            ax.plot(X[i, 0], X[i, 1], c='red', marker='o', linestyle='', ms=12, label=news)
        elif news == 'wp':
            ax.plot(X[i, 0], X[i, 1], c='blue', marker='o', linestyle='', ms=12, label=news)
        else:
            ax.plot(X[i, 0], X[i, 1], c='orange', marker='o', linestyle='', ms=12, label=news)
    plt.scatter(kmeans_model.cluster_centers_[:, 0], kmeans_model.cluster_centers_[:, 1],
                c='black', s=100, alpha=0.6)
    magenta_patch = mpatches.Patch(color='magenta', label='fox')
    cyan_patch = mpatches.Patch(color='cyan', label='cnn')
    green_patch = mpatches.Patch(color='green', label='bbc')
    red_patch = mpatches.Patch(color='red', label='bb')
    blue_patch = mpatches.Patch(color='blue', label='wp')
    orange_patch = mpatches.Patch(color='orange', label='ap')
    black_patch = mpatches.Patch(color='black', label='centroids')
    plt.legend(handles=[magenta_patch, cyan_patch, red_patch, green_patch,
                        red_patch, blue_patch, orange_patch, black_patch])
    plt.show()


# class StemmerTokenizer(object):
#     def __init__(self):
#         self.porter_stemmer = PorterStemmer()
#         self.treebank_tokenizer = TreebankWordTokenizer()
#
#     def __call__(self, sentence):
#         return [self.porter_stemmer.stem(token) for token in self.treebank_tokenizer.tokenize(sentence)
#                 if token not in eng_stopwords]
#
#
# def KMeansClustering(quote_dict, clusters=2):
#     """Returns a pandas data frame containing the quote_dict and cluster label."""
#     count_vectorizer = CountVectorizer(tokenizer=StemmerTokenizer(), lowercase=True)
#     X = count_vectorizer.fit_transform(quote_dict.values()).toarray()
#     kmeans_model = KMeans(n_clusters=clusters).fit(X)
#     y = kmeans_model.predict(X)
#     kmeans_df = pd.DataFrame.from_dict(quote_dict, orient='index', columns=['sentence'])
#     kmeans_df["cluster"] = kmeans_model.labels_
#     return X, y, kmeans_model, kmeans_df
#
#
# def KMeansClusteringPlot(X, y, kmeans_model, quote_dict):
#     """Show clusters with centroids from k-means."""
#     plt.scatter(X[:, 0][0], X[:, 1][0], s=200, color='blue', label=[k for k in quote_dict.keys()][0])
#     plt.scatter(X[:, 0][1], X[:, 1][1], s=200, color='red', label=[k for k in quote_dict.keys()][1])
#     plt.scatter(X[:, 0][2], X[:, 1][2], s=200, color='green', label=[k for k in quote_dict.keys()][2])
#     centers = kmeans_model.cluster_centers_
#     plt.scatter(centers[:, 0], centers[:, 1], c='black', s=100, alpha=0.6)
#     plt.legend()
#     plt.show()
#
#
# if __name__ == "__main__":
#     quote_dict = {'cnn': 'witch hunt', 'fox': 'donald trump says this is a witch hunt',
#                 'bbc': 'donald trump is a crookity crook who should be impeached'}
#
#     kmeans_elbow = KMeansClusteringElbowCurve(quote_dict)
#
#     X, y, kmeans_model, kmeans_df = KMeansClustering(quote_dict)
#     print(kmeans_df)
#
#     kmeans_plot = KMeansClusteringPlot(X, y, kmeans_model, quote_dict)
