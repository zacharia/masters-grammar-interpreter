#!/bin/bash
#A script to run the python interpreter using standard arguments.

python interpreter.py -i input -m 5 -p -v $@ | less -S

