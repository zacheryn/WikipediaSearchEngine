"""REST API functions."""
import re
from math import sqrt
import flask
import index


def load_index():
    """Load stopwords and pagerank into memory."""
    # Load stopwords
    #
    # Format: list of words
    path = index.app.config["STOPWORDS_FILE"]
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            index.app.config["STOPWORDS"].append(line.replace("\n", ""))

    # Load pageranks
    #
    # Format: dictionary where doc id is key and pagerank is value
    path = index.app.config["PAGERANK_FILE"]
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.replace("\n", "")
            index.app.config["PAGERANKS"][line[:4]] = float(line[5:])

    # Load inverted index
    #
    # Format: dictionary where the term is key and a list with the
    # first element being the tf-idf and the following a set of three for
    # doc id, term frequency, and squared normalization respectively
    path = index.app.config["INVERTED_INDEX_FOLDER"]
    path = path/index.app.config["INDEX_PATH"]
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line[:-1]
            line = line.split(" ")
            term = [float(line[1])]
            for i in range(2, len(line), 3):
                term.append(line[i])
                term.append(int(line[i+1]))
                term.append(float(line[i+2]))
            index.app.config["INVERTED_INDEX"][line[0]] = term


@index.app.route("/api/v1/")
def services():
    """Return a list of services availible in the api."""
    context = {
        "hits": "/api/v1/hits/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context)


def remove_bad_input(query: list):
    """Remove unwanted and bad input from query."""
    for i in range(len(query) - 1, -1, -1):
        try:
            if query[i] in index.app.config["STOPWORDS"]:
                query.pop(i)
            elif index.app.config["INVERTED_INDEX"][query[i]][0] == 0:
                query.pop(i)
        except KeyError:
            continue


def intersection(lst1: list, lst2: list) -> list:
    """Find the intersection between two sorted lists."""
    i = 0
    j = 0
    result = []
    while i < len(lst1) and j < len(lst2):
        if lst1[i] < lst2[j]:
            i += 1
        elif lst1[i] > lst2[j]:
            j += 1
        else:
            result.append(lst1[i])
            i += 1
            j += 1

    return result


def get_docs(query: list) -> list:
    """Return a list of docs that contain all terms in the query."""
    # Base case
    if len(query) == 0:
        return []

    # Add docs only containing every word from query
    docs = []
    try:
        for i in range(1,
                       len(index.app.config["INVERTED_INDEX"][query[0]]),
                       3):
            docs.append(index.app.config["INVERTED_INDEX"][query[0]][i])
        for i in range(1, len(query)):
            tmp_docs = []
            for j in range(1,
                           len(index.app.config["INVERTED_INDEX"][query[i]]),
                           3):
                tmp = index.app.config["INVERTED_INDEX"][query[i]][j]
                tmp_docs.append(tmp)
            docs = intersection(docs, tmp_docs)
    except KeyError:
        docs = []

    return docs


def make_query_vec(query: list) -> list:
    """Calculate the query vector."""
    qvec = []
    known_terms = []
    for i, word in enumerate(query):
        if word in known_terms:
            continue
        known_terms.append(word)
        count = float(1)
        for j in range(i+1, len(query)):
            if word == query[j]:
                count += 1
        qvec.append(count * index.app.config["INVERTED_INDEX"][word][0])

    return qvec


def make_doc_vec(query: list, doc: str) -> list:
    """Calculate the document vector."""
    dvec = []
    known_terms = []
    for word in query:
        if word in known_terms:
            continue
        known_terms.append(word)
        for j in range(1,
                       len(index.app.config["INVERTED_INDEX"][word]),
                       3):
            if index.app.config["INVERTED_INDEX"][word][j] == doc:
                prod = index.app.config["INVERTED_INDEX"][word][j+1]
                prod *= index.app.config["INVERTED_INDEX"][word][0]
                dvec.append(prod)
                break

    return dvec


def tfidf(query: list, doc: str) -> float:
    """Calculate the tf-idf of a doc for a query."""
    qvec = make_query_vec(query)
    dvec = make_doc_vec(query, doc)

    # Calculate the dot product of the two vectors
    dot = 0
    for i, q in enumerate(qvec):
        dot += q * dvec[i]

    # Calculate the normalization factors
    qmag = 0
    for q in qvec:
        qmag += (q * q)
    qmag = sqrt(qmag)

    dmag = 0
    for i in range(1, len(index.app.config["INVERTED_INDEX"][query[0]]), 3):
        if index.app.config["INVERTED_INDEX"][query[0]][i] == doc:
            dmag = sqrt(index.app.config["INVERTED_INDEX"][query[0]][i+2])
            break

    # Calculate and return tf-idf
    return dot / (qmag * dmag)


def score(query: list, doc: str, weight: float) -> float:
    """Calculate the score of a doc for a query."""
    return (weight * index.app.config["PAGERANKS"][doc])\
        + ((1 - weight) * tfidf(query, doc))


def sorted_scores(query: list, docs: list, weight: float) -> list:
    """Return a reverse sorted list of scores for each doc."""
    # Calculate all scores
    scores = {}
    for doc in docs:
        scores[score(query, doc, weight)] = doc

    # Sort and return them
    result = []
    for s in sorted(scores.keys(), reverse=True):
        result.append(scores[s])
        result.append(s)

    return result


@index.app.route("/api/v1/hits/")
def hits():
    """Return the hits from a search query."""
    # Get the query parameters
    query = flask.request.args.get(
        "q",
        type=str
    )

    weight = flask.request.args.get(
        "w",
        0.5,
        float
    )

    # Clean the query
    query = re.sub(r"[^a-zA-Z0-9 ]+", "", query)
    query = query.casefold()
    query = query.split()
    remove_bad_input(query)

    # Get the valid doc ids for the query
    docs = get_docs(query)

    # Get the scorse for the docs
    results = []
    scores = sorted_scores(query, docs, weight)
    for i in range(0, len(scores), 2):
        h = {
            "docid": int(scores[i]),
            "score": scores[i+1]
        }
        results.append(h)

    # Send response
    context = {
        "hits": results,
    }
    return flask.jsonify(**context)
