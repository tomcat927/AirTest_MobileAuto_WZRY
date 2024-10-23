#!/usr/bin/env bash
python3 wzry.py config.lin.txt "$@"  2>&1 | tee result
