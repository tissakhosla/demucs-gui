#! /bin/bash

while true
  do
    for f in $(cat fpipe)
      do demucs $f
    done
done

