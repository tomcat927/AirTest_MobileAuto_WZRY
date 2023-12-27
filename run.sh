cat result >> result.bak.txt
python3 -u object.py  2>&1 | tee result
