#!/bin/bash
# "I 가 맨 앞이면 항상 가능한가" 를 탐침한다.
# 사용법: ./scripts/ifirst-probe.sh <케이스파일> <출력파일>   (PAR, CAP, TMO 환경변수)
#
# 탐침이지 전수가 아니다. 840 접두사 전부가 아니라 **지금까지 실패를 낸 접두사** 만 붙인다.
# 그래서 "실패 0" 은 "반례가 이 접두사들에는 없다" 는 뜻이지 정리가 아니다.
#
# 이미 출력에 있는 케이스는 건너뛴다 (재개 가능).
set -u

export SOLVER=${SOLVER:-./bin/fix4}
export CAP=${CAP:-93000000}     # fix4 표 한계가 93,952,404 이라 그 위는 의미가 없다
export TMO=${TMO:-5400}
par=${PAR:-1}

cases=$1
out=$2
touch "$out"

probe_one() {
  b1=$1; b2=$2
  r=$(timeout "$TMO" "$SOLVER" "$b1$b2" "$CAP" 2>/dev/null)
  states=$(printf '%s' "$r" | sed -n 's/.*states \([0-9]*\).*/\1/p')
  case "$r" in
    *"PC POSSIBLE"*)  echo "$b1 $b2 OK $states" ;;
    *"INCONCLUSIVE"*) echo "$b1 $b2 CAP $states" ;;
    "")               echo "$b1 $b2 TIMEOUT -" ;;
    *)                echo "$b1 $b2 FAIL $states" ;;
  esac
}
export -f probe_one

todo=$(mktemp)
while read -r b1 b2; do
  [ -z "${b1:-}" ] && continue
  grep -q "^$b1 $b2 " "$out" 2>/dev/null || echo "$b1 $b2"
done < "$cases" > "$todo"
echo "남은 $(grep -c . "$todo") / 전체 $(grep -c . "$cases")"

xargs -a "$todo" -n 2 -P "$par" bash -c 'probe_one "$0" "$1"' >> "$out"
rm -f "$todo"
echo "=== 집계 ==="
awk '{print $3}' "$out" | sort | uniq -c
echo "=== FAIL 이 있으면 반례다 ==="
grep " FAIL " "$out" || echo "없음"
