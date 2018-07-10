#!/bin/bash
PYTHONPATH=../:. python testcases-2.py > testcases-2.my-output
python special_diff.py testcases-2.output testcases-2.my-output
