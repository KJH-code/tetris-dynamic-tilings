#!/bin/bash
# bag1 을 고정하고 bag2 접두사 목록을 훑어 PC 가능 여부를 파일로 적는다.
# 사용법: ./scripts/survey.sh <bag1 7 자> <접두사 목록 파일> <출력 파일>
# 출력 한 줄 = "<접두사> OK|FAIL|CAP|TIMEOUT". CAP 와 TIMEOUT 은 결론이 아니므로
# 반드시 상한을 올려 재실행할 것 (SOLVER 로 fix5 로 바꿔 교차검증도 가능).
#
# 원래 이 스크립트는 ./fix2 를 불렀으나 fix2.cpp 는 레포에 없다 (2026-09-15 감사).
# 확정 결과는 fix4 로 전부 재현되므로 기본 솔버를 fix4 로 바꿨다.
solver=${SOLVER:-./bin/fix4}
cap=${CAP:-20000000}
b1=$1; list=$2; out=$3
: > "$out"
while read -r b; do
  [ -z "$b" ] && continue
  r=$(timeout "${TIMEOUT:-70}" "$solver" "${b1}${b}" "$cap" 2>/dev/null)
  case "$r" in
    *"PC POSSIBLE"*) echo "$b OK" >> "$out" ;;
    *"INCONCLUSIVE"*) echo "$b CAP" >> "$out" ;;
    "") echo "$b TIMEOUT" >> "$out" ;;
    *) echo "$b FAIL" >> "$out" ;;
  esac
done < "$list"
