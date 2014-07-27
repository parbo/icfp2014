#!/bin/sh

mkdir -p solution
./code/lml/lmanlisp.py code/lml/ai_1.lml > solution/lambdaman.gcc
./code/ghost/ghost.py code/ghost/ai_0.ghc > solution/ghost0.ghc
