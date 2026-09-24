#!/bin/bash
# bag1 을 고정하고 bag2 접두사 목록을 fix4 로 훑는다 (1 차 선별, 상한 8M).
# 사용법: ./scripts/scan.sh <bag1 7 자> <접두사 목록 파일> <출력 파일>
# 출력 한 줄 = "<접두사> OK|FAIL|CAP|TIMEOUT". CAP/TIMEOUT 은 결론이 아니다.
b1=$1; : > "$3"
while read -r b; do
  [ -z "$b" ] && continue
  r=$(timeout 45 ${SOLVER:-./bin/fix4} "${b1}${b}" 8000000 2>/dev/null)
  case "$r" in
    *"PC POSSIBLE"*) echo "$b OK" >> "$3" ;;
    *"INCONCLUSIVE"*) echo "$b CAP" >> "$3" ;;
    "") echo "$b TIMEOUT" >> "$3" ;;
    *) echo "$b FAIL" >> "$3" ;;
  esac
done < "$2"
