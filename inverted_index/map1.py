#!/usr/bin/env python3
"""map 1."""
import pathlib
import re
import sys

import bs4

stopwords = []
with open(pathlib.Path("stopwords.txt"), "r", encoding="utf-8") as file:
    for line in file:
        stopwords.append(line.replace("\n", ""))

# Open and read from one HTML document at a time
for line in sys.stdin:
    # Each line is a path to a document from the dataset
    # Documents are stored at <INPUT_DIR>/crawl/<doc_id>.html
    doc_path = pathlib.Path(line.strip())

    # Get doc_id from filename
    doc_id = line.split(".")[0][-4:]

    # Read document body from file
    text = doc_path.read_text(encoding="utf-8")

    # Configure Beautiful Soup parser
    soup = bs4.BeautifulSoup(text, "html.parser")

    # Parse text from document
    text = soup.text

    # Clean input
    text = re.sub(r"[^a-zA-Z0-9 ]+", "", text)
    text = text.casefold()
    text = text.split()

    for i in range(len(text) - 1, -1, -1):
        if text[i] in stopwords:
            text.pop(i)

    # Output Map
    for term in text:
        print(f"{term}\t{doc_id}")
