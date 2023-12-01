#!/usr/bin/env python3
"""Reduce 2."""
import sys
import itertools


def combine_docs(key, group):
    """Combine same terms from different docs to complete the index."""
    s = f"{key}"
    idf_printed = False
    d = {}
    for line in group:
        line = line.partition("\t")[2][1:-2].split(", ")
        line[2] = int(line[2])
        line[3] = float(line[3])
        line[4] = line[4][1:-1]
        d[line[4]] = line
    for doc_id in sorted(d.keys()):
        print(s, end=" ")
        if not idf_printed:
            idf_printed = True
            print(f"{float(d[doc_id][1])}", end=" ")
        s = f"{d[doc_id][4]} {d[doc_id][2]} {d[doc_id][3]}"
    print(s)


def keyfunc(line):
    """Return the key from a TAB-delimited key-value pair."""
    return line.partition("\t")[2][1:-2].split(", ")[0][1:-1]


def main():
    """Divide sorted lines into groups that share a key."""
    for key, group in itertools.groupby(sys.stdin, keyfunc):
        combine_docs(key, group)


if __name__ == "__main__":
    main()
