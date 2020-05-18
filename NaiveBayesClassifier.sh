#!/bin/bash

if ! [ -x "$(command -v python3)" ]; then
  python final.py $1 $2
  exit 0
else
    python3 final.py $1 $2
fi