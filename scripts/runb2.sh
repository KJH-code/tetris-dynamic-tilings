#!/bin/bash
# usage: ./runb2.sh <bag1 7 letters> <file of bag2 prefixes> <out>
b1=$1; list=$2; out=$3
: > "$out"
while read -r b; do
  [ -z "$b" ] && continue
  r=$(timeout 90 ./fix "${b1}${b}" 2>/dev/null)
  if [ -z "$r" ]; then
    echo "$b TIMEOUT" >> "$out"
  else
    case "$r" in
      *"PC POSSIBLE"*) echo "$b OK" >> "$out" ;;
      *"INCONCLUSIVE"*) echo "$b CAP" >> "$out" ;;
      *) echo "$b FAIL" >> "$out" ;;
    esac
  fi
done < "$list"
