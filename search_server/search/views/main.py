"""Search page with server-side dynamics."""
from threading import Thread, Lock
import flask
import requests
import search


def base():
    """Return the base homepage (no query made)."""
    context = {
        "query_made": False,
        "top": [],
        "query": "",
        "weight": 0.5
    }
    return flask.render_template("results.html", **context)


def call_api(results: list, url: str, query: str, weight: float, lock: Lock):
    """Make a GET request to the given API with query and weight."""
    payload = {
        "q": query,
        "w": weight
    }
    r = requests.get(url, params=payload, timeout=10)
    with lock():
        results.append(r.json()["hits"])


def merge_docs(results: list) -> list:
    """Combine the three lists in results."""
    i = 0
    j = 0
    tmp_top = []
    while i < len(results[0]) and j < len(results[1]):
        if results[0][i]["score"] > results[1][j]["score"]:
            tmp_top.append(results[0][i])
            i += 1
        else:
            tmp_top.append(results[1][j])
            j += 1
    tmp_top = tmp_top + results[0][i:] + results[1][j:]
    if len(tmp_top) > 10:
        tmp_top = tmp_top[:10]
    i = 0
    j = 0
    top = []
    while i < len(tmp_top) and j < len(results[2]):
        if tmp_top[i]["score"] > results[2][j]["score"]:
            top.append(tmp_top[i])
            i += 1
        else:
            top.append(results[2][j])
            j += 1
    top = top + tmp_top[i:] + results[2][j:]
    if len(top) > 10:
        top = top[:10]

    return top


@search.app.route("/")
def index():
    """Return the index."""
    query = flask.request.args.get("q", type=str)

    # If no query made, return the homepage
    if query is None:
        return base()

    weight = flask.request.args.get("w", type=float, default=0.5)

    # Call APIs across multiple threads for speed
    results = []
    threads = []
    lock = Lock
    for url in search.app.config["SEARCH_INDEX_SEGMENT_API_URLS"]:
        t = Thread(target=call_api, args=[results, url, query, weight, lock])
        t.start()
        threads.append(t)

    # Join API call threads
    for t in threads:
        t.join()

    # merge the results
    top = merge_docs(results)

    # Connect to database
    connection = search.model.get_db()

    # Get doc details
    for i, doc in enumerate(top):
        cur = connection.execute(
            "SELECT title, summary, url "
            "FROM Documents "
            "WHERE docid = ?",
            (doc["docid"],)
        )
        details = cur.fetchone()
        top[i]["title"] = details["title"]
        top[i]["summary"] = details["summary"] if details["summary"]\
            != "" else "No summary available"
        top[i]["url"] = details["url"]

    # Set up context
    context = {
        "query_made": True,
        "top": top,
        "query": query,
        "weight": weight
    }

    # Return template
    return flask.render_template("results.html", **context)
