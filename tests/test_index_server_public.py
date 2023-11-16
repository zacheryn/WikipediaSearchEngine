"""Public Index Server tests."""
import utils


def test_multiple_terms(index_client):
    """Multiple word query.

    The PageRank weight parameter 'w' is missing.  The default value 0.5 should
    be used by the Index Server.

    'index_client' is a fixture fuction that provides a Flask test server
    interface. It is implemented in conftest.py and reused by many tests.
    Docs: https://docs.pytest.org/en/latest/fixture.html

    """
    # Query the REST API
    response = index_client.get("/api/v1/hits/?q=water+bottle")
    assert response.status_code == 200

    # Compare actual hits to solution hits
    hits_actual = response.get_json()["hits"]
    hits_solution = [
        {"docid": 2817, "score": 0.006633078998361841},
        {"docid": 3021, "score": 0.0035012082579604716},
        {"docid": 1596, "score": 0.0031862446890546323},
        {"docid": 1038, "score": 0.003166637585248239},
        {"docid": 1101, "score": 0.002295609163205213},
        {"docid": 1791, "score": 0.0018750947588252825}
    ]
    utils.assert_rest_api_hit_eq(hits_actual, hits_solution)


def test_special_characters(index_client):
    """Special characters in query.

    'index_client' is a fixture fuction that provides a Flask test server
    interface. It is implemented in conftest.py and reused by many tests.
    Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Query the REST API
    response = index_client.get("/api/v1/hits/?q=the+^most+@@had@@oop&w=0")
    assert response.status_code == 200

    # Compare actual hits to solution hits
    hits_actual = response.get_json()["hits"]
    hits_solution = [
        {"docid": 2373, "score": 0.048881491721265824},
        {"docid": 342, "score": 0.02217589203170991},
        {"docid": 2820, "score": 0.019571269903245845},
        {"docid": 2658, "score": 0.015979524172990506},
        {"docid": 582, "score": 0.014668692270570124},
        {"docid": 1899, "score": 0.010792173357746569},
        {"docid": 990, "score": 0.004593623060283451}
    ]
    utils.assert_rest_api_hit_eq(hits_actual, hits_solution)


def test_stopwords(index_client):
    """Stopwords in query.

    'index_client' is a fixture fuction that provides a Flask test server
    interface. It is implemented in conftest.py and reused by many tests.
    Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Query the REST API
    response = index_client.get("/api/v1/hits/?q=the+most+hadoop&w=0")
    assert response.status_code == 200

    # Compare actual hits to solution hits
    hits_actual = response.get_json()["hits"]
    hits_solution = [
        {"docid": 2373, "score": 0.048881491721265824},
        {"docid": 342, "score": 0.02217589203170991},
        {"docid": 2820, "score": 0.019571269903245845},
        {"docid": 2658, "score": 0.015979524172990506},
        {"docid": 582, "score": 0.014668692270570124},
        {"docid": 1899, "score": 0.010792173357746569},
        {"docid": 990, "score": 0.004593623060283451}
    ]
    utils.assert_rest_api_hit_eq(hits_actual, hits_solution)


def test_term_not_in_index(index_client):
    """Query term not in inverted index.

    'index_client' is a fixture fuction that provides a Flask test server
    interface. It is implemented in conftest.py and reused by many tests.
    Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    response = index_client.get("/api/v1/hits/?q=issued+aaaaaaa&w=0.5")
    assert response.status_code == 200
    assert response.get_json() == {"hits": []}
