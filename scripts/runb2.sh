#!/bin/bash
# survey.sh 와 같은 훑기인데 솔버 기본 상한(3M)을 그대로 쓴다. data/b2all.out 을 만든 스크립트.
# 사용법: ./scripts/runb2.sh <bag1 7 자> <접두사 목록 파일> <출력 파일>
# 출력 한 줄 = "<접두사> OK|FAIL|CAP|TIMEOUT". b2all.out 의 CAP 4 건이 바로 이 낮은 상한 탓이다.
#
# 원래 ./fix 를 불렀으나 fix.cpp 는 레포에 없다 (2026-09-15 감사). fix4 로 바꿨다.
solver=${SOLVER:-./bin/fix4}
b1=$1; list=$2; out=$3
: > "$out"
while read -r b; do
  [ -z "$b" ] && continue
  r=$(timeout "${TIMEOUT:-90}" "$solver" "${b1}${b}" 2>/dev/null)
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
