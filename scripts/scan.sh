#!/bin/bash
b1=$1; : > "$3"
while read -r b; do
  [ -z "$b" ] && continue
  r=$(timeout 45 ./fix4 "${b1}${b}" 8000000 2>/dev/null)
  case "$r" in
    *"PC POSSIBLE"*) echo "$b OK" >> "$3" ;;
    *"INCONCLUSIVE"*) echo "$b CAP" >> "$3" ;;
    "") echo "$b TIMEOUT" >> "$3" ;;
    *) echo "$b FAIL" >> "$3" ;;
  esac
done < "$2"
