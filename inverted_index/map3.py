#!/usr/bin/env python3
"""map 2."""
import sys

for line in sys.stdin:
    doc_id = int(line.partition("\t")[0])
    tup = line.partition("\t")[2][1:-2].split(", ")
    tup[0] = tup[0][1:-1]
    tup[1] = float(tup[1])
    tup[2] = int(tup[2])
    tup[3] = float(tup[3])
    tup = tuple(tup) + (line.partition("\t")[0],)
    print(f"{doc_id % 3}\t{tup}")
