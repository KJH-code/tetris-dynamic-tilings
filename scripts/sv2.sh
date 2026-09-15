#!/bin/bash
# survey.sh 와 같은 일을 더 짧은 상한/타임아웃으로 한다 (1 차 선별용).
# 사용법: ./scripts/sv2.sh <bag1 7 자> <접두사 목록 파일> <출력 파일>
# 출력 한 줄 = "<접두사> OK|FAIL|CAP|TIMEOUT". 선별이 목적이므로 CAP 가 많이 나온다 -- 정상이다.
#
# 기본 솔버를 ./fix2 에서 fix4 로 바꿨다. fix2.cpp 는 레포에 없다 (2026-09-15 감사).
solver=${SOLVER:-./bin/fix4}
cap=${CAP:-15000000}
b1=$1; list=$2; out=$3
: > "$out"
while read -r b; do
  [ -z "$b" ] && continue
  r=$(timeout "${TIMEOUT:-60}" "$solver" "${b1}${b}" "$cap" 2>/dev/null)
  case "$r" in
    *"PC POSSIBLE"*) echo "$b OK" >> "$out" ;;
    *"INCONCLUSIVE"*) echo "$b CAP" >> "$out" ;;
    "") echo "$b TIMEOUT" >> "$out" ;;
    *) echo "$b FAIL" >> "$out" ;;
  esac
done < "$list"
