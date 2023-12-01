#!/usr/bin/env python3
"""Reduce 2."""
import sys
import itertools


def calc_normalization(key, group):
    """Calculate the squared normalization factor for a document."""
    norm = 0
    lines = []
    for line in group:
        line = line.partition("\t")[2][1:-2].split(", ")
        line[0] = line[0][1:-1]
        line[1] = float(line[1])
        line[2] = int(line[2])
        line = tuple(line)
        lines.append(line)
        norm += (float(line[1]) * float(line[1]) *
                 float(line[2]) * float(line[2]))
    for line in lines:
        print(f"{key}\t{line + (norm,)}")


def keyfunc(line):
    """Return the key from a TAB-delimited key-value pair."""
    return line.partition("\t")[0]


def main():
    """Divide sorted lines into groups that share a key."""
    for key, group in itertools.groupby(sys.stdin, keyfunc):
        calc_normalization(key, group)


if __name__ == "__main__":
    main()
