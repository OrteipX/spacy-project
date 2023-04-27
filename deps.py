#!/usr/bin/python3
# Name: deps.py
# Date: Nov 01, 2022

import os

deps_cmds = [
    "python3 -m pip install spacy==3.4.2",
    "python3 -m spacy download en_core_web_sm"
]

for dep in deps_cmds:
    os.system(dep)
