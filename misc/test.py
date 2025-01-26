#! /usr/bin/env python

import argparse 
from pathlib import Path
import random

parser = argparse.ArgumentParser()
parser.add_argument("--seed")
parser.add_argument("filename") 
parser.add_argument("--mod1", action="store_true") 
parser.add_argument("--mod2", action="store_true")
args = parser.parse_args() 

print(f"calling solver with seed {args.seed}")
if args.mod1: 
    print("with mod 1")

if args.mod2:
    print("with mod 2")
    
print(Path(args.filename).read_text())

print(f"cost: {random.randint(0, 10)}")
