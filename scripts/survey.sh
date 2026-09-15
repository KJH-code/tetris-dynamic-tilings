#!/bin/bash
# usage: ./survey.sh <bag1> <prefix list> <out>
b1=$1; : > "$3"
while read -r b; do
  [ -z "$b" ] && continue
  r=$(timeout 70 ./fix2 "${b1}${b}" 20000000 2>/dev/null)
  case "$r" in
    *"PC POSSIBLE"*) echo "$b OK" >> "$3" ;;
    *"INCONCLUSIVE"*) echo "$b CAP" >> "$3" ;;
    "") echo "$b TIMEOUT" >> "$3" ;;
    *) echo "$b FAIL" >> "$3" ;;
  esac
done < "$2"
