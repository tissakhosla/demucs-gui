#! /bin/bash

while true
  do
    for f in $(cat fpipe)
      do demucs -n htdemucs_ft $f
    done
done

