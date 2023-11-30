#!/usr/bin/env python3
"""Reduce 1."""
import sys
import itertools
from math import log10

def calc_idf(key, group, doc_tot):
    """Reduce one group."""
    doc_count = float(0)
    docs = ()
    for doc_id in group:
        docs = docs + (doc_id,)
        doc_count += 1
    idf = log10(doc_tot / doc_count)
    print(f"{key} {idf}")


def keyfunc(line):
    """Return the key from a TAB-delimited key-value pair."""
    return line.partition("\t")[0]


def main():
    """Divide sorted lines into groups that share a key."""
    doc_tot = 0
    with open("total_document_count.txt", "r", encoding="utf-8") as file:
        for line in file:
            doc_tot = float(line)
            break

    for key, group in itertools.groupby(sys.stdin, keyfunc):
        calc_idf(key, group, doc_tot)


if __name__ == "__main__":
    main()
