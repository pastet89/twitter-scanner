#!/bin/bash
pkill -f twitter.py
nohup python twitter.py &
exit 0
