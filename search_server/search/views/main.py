"""Search page with server-side dynamics."""
import flask
from threading import Thread, Lock
from heapq import merge
import requests
import search


def base():
    """Return the base homepage (no query made)."""
    context = {}
    return flask.render_template("main.html", **context)


def call_api(results: list, url: str, query: str, weight: float, lock: Lock):
    """Make a GET request to the given API with query and weight."""
    payload = {
        "q": query,
        "w": weight
    }
    r = requests.get(url, params=payload)
    with lock:
        results.append(r.json()["hits"])


def keyfunc(elt):
    """Key function for heapq merge."""
    return elt["score"]


@search.app.route("/")
def index():
    """Return the index."""
    query = flask.request.args.get("q", type=str)

    # If no query made, return the homepage
    if query is None:
        return base()
    
    weight = flask.request.args.get("w", type=float)

    # Call APIs across multiple threads for speed
    results = []
    threads = []
    lock = Lock
    for url in search.app.config["SEARCH_INDEX_SEGMENT_API_URLS"]:
        t = Thread(target=call_api, args=[results, url, query, weight, lock])
        t.run()
        threads.append(t)

    # Join API call threads
    for t in threads:
        t.join()

    # merge the results
    top = list(merge(results[0], results[1], results[2], key=keyfunc))
    if len(top) > 10:
        top = top[:10]

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
        top[i]["summary"] = details["summary"]
        top[i]["url"] = details["url"]

    # Set up context
    context = {
        "top": top
    }

    # Return template
    return flask.render_template("results.html", **context)
