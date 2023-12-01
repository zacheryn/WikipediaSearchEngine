#!/usr/bin/env python3
"""map 2."""
import sys

for line in sys.stdin:
    tup = line.partition("\t")[0][1:-1].split(", ")
    tup[0] = tup[0][1:-1]
    tup[1] = float(tup[1])
    tf = int(line.partition("\t")[2][:-1])
    doc_id = tup.pop()[1:-1]
    tup.append(tf)
    print(f"{doc_id}\t{tuple(tup)}")
