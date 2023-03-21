#! /bin/bash
IFS=''
while true
  do
    for dcmd in $(cat ~/demucs-gui/fpipe)
      do eval $dcmd
    done
done

