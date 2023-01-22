#! /bin/bash
IFS=''
while true
  do
    for dcmd in $(cat fpipe)
      do eval $dcmd
    done
done

