#!/usr/bin/env bash
python3 wzry.py config.lin.yaml "$@"  2>&1 | tee result
