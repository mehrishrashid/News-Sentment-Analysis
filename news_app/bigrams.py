# set up and dependencies
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from matplotlib import pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download("stopwords")

pd.set_option("display.max_rows", None)

path = "files/headlines.csv"

# Read news article data into dataframe and exclude rows with NaN in "lead_paragraph" column (200+ rows excluded)
df = pd.read_csv(path)
df2 = df[df["lead_paragraph"].notna()]

# Bigrams
# Use TF-IDF method to generate bigrams and trigrams
abstract = df["abstract"]
headline = df["headline"]
lead = df["lead_paragraph"]

stoplist = stopwords.words("english")

# Get ABSTRACT bigrams - Applying TFIDF
# vectorizer2 = TfidfVectorizer(stop_words=stoplist, ngram_range=(2, 2))
# X2 = vectorizer2.fit_transform(txt1)
# scores = X2.toarray()
# print("Scores : \n", scores)

# Get LEAD PARAGRAPH bigrams
# vectorizer2 = CountVectorizer(stop_words=stoplist, ngram_range=(2, 2))
# X2 = vectorizer2.fit_transform(lead_paragraph)
# features2 = vectorizer2.get_feature_names()
# print("X2 : \n", X2.toarray())

# Get HEADLINE bigrams
vectorizer2 = CountVectorizer(stop_words=stoplist, ngram_range=(2, 2))
X2 = vectorizer2.fit_transform(headline)
features2 = vectorizer2.get_feature_names()
print("X2 : \n", X2.toarray())

# Getting top ranking features - bigrams
sums2 = X2.sum(axis=0)
data2 = []
for col, term in enumerate(features2):
    data2.append((term, sums2[0, col]))
ranking2 = pd.DataFrame(data2, columns=["term", "rank"])
words2 = ranking2.sort_values("rank", ascending=False)
print("Words : \n", words2.head(20))

# Get HEADLINE trigrams
vectorizer3 = CountVectorizer(stop_words=stoplist, ngram_range=(3, 3))
X3 = vectorizer3.fit_transform(headline)
features3 = vectorizer3.get_feature_names()
print("X3 : \n", X3.toarray())

# Getting top ranking features - trigrams
sums3 = X3.sum(axis=0)
data3 = []
for col, term in enumerate(features3):
    data3.append((term, sums3[0, col]))
ranking3 = pd.DataFrame(data3, columns=["term", "rank"])
words3 = ranking3.sort_values("rank", ascending=False)
print("Words : \n", words3.head(20))

rank_df2 = words2.head(n=50)
rank_df3 = words3.head(n=50)

# Plots
# rank_df.plot(x="term", y="rank", style="o", rot=90)

# Bigram bubble chart
fig2 = px.scatter(
    rank_df2,
    x="term",
    y="rank",
    hover_name="term",
    log_y=True,
    # text="term",
    size="rank",
    color="term",
    size_max=45,
    template="plotly_white",
    title="Bigram similarity and frequency",
    labels={"words": "Avg. Length<BR>(words)"},
    color_continuous_scale=px.colors.sequential.Sunsetdark,
)
fig2.update_traces(marker=dict(line=dict(width=1, color="Gray")))
fig2.update_xaxes(visible=True)
fig2.update_yaxes(visible=True)

# Create and add slider
# steps = []
# for i in range(len(fig.data)):
#     step = dict(
#         method="update",
#         args=[{"visible": [False] * len(fig.data)},
#               {"title": "Slider switched to step: " + str(i)}],  # layout attribute
#     )
#     step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
#     steps.append(step)

# sliders = [dict(
#     active=10,
#     currentvalue={"prefix": "Frequency: "},
#     pad={"t": 50},
#     steps=steps
# )]

# fig.update_layout(
#     sliders=sliders
# )

fig2.show()

# Trigram bubble chart
fig3 = px.scatter(
    rank_df3,
    x="term",
    y="rank",
    hover_name="term",
    log_y=True,
    # text="term",
    size="rank",
    color="term",
    size_max=45,
    template="plotly_white",
    title="Bigram similarity and frequency",
    labels={"words": "Avg. Length<BR>(words)"},
    color_continuous_scale=px.colors.sequential.Sunsetdark,
)
fig3.update_traces(marker=dict(line=dict(width=1, color="Gray")))
fig3.update_xaxes(visible=True)
fig3.update_yaxes(visible=True)

# Create and add slider
# steps = []
# for i in range(len(fig.data)):
#     step = dict(
#         method="update",
#         args=[{"visible": [False] * len(fig.data)},
#               {"title": "Slider switched to step: " + str(i)}],  # layout attribute
#     )
#     step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
#     steps.append(step)

# sliders = [dict(
#     active=10,
#     currentvalue={"prefix": "Frequency: "},
#     pad={"t": 50},
#     steps=steps
# )]

# fig.update_layout(
#     sliders=sliders
# )

fig3.show()

# Scatter plot of n-grams
# trigram = rank_df["term"]
# rank = rank_df["rank"]

# fig = go.Figure(
#     data=go.Scattergl(
#         x=trigram,
#         y=rank,
#         mode="markers",
#         marker=dict(color=rank, colorscale="Viridis", line_width=1),
#     )
# )
# fig.show()

# Bigram TF-IDF Logistic Regression
# bigram_tfidf_logistic_regression = make_pipeline(
#     CountVectorizer(
#         stop_words='english',
#         ngram_range=(1,2)
#     ),
#     TfidfTransformer(),
#     LogisticRegression()
# )

# bigram_tfidf_logistic_regression.fit(X_train, y_train)

# print(f'Accuracy: {bigram_tfidf_logistic_regression.score(X_test, y_test)} \n')
# print(classification_report(y_test, bigram_tfidf_logistic_regression.predict(X_test)))
