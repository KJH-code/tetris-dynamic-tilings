#!/bin/bash
# bag1sweep.sh 가 남긴 CAP/TIMEOUT 케이스를 큰 상한으로 재실행해 확정한다.
# 사용법: ./scripts/capresolve.sh <케이스 파일 "bag1 bag2" 줄> <출력 파일>
# 출력 한 줄 = "<bag1> <bag2> OK|FAIL|CAP|TIMEOUT <상태 수>". 이미 있는 케이스는 건너뛴다.
#
# **CAP 은 결론이 아니다.** 1 단계의 상한(8M)에서 미결인 케이스만 여기로 온다.
# 여기서도 CAP 이 남으면 그건 여전히 미결이고, 더 큰 표를 가진 솔버가 필요하다.
# 환경변수: SOLVER(기본 ./bin/fix4) CAP(200000000) TMO(600) PAR(4)
set -u

export SOLVER=${SOLVER:-./bin/fix4}
export CAP=${CAP:-200000000}
export TMO=${TMO:-600}
par=${PAR:-4}

cases=$1
out=$2
touch "$out"

resolve_one() {
  b1=$1
  b2=$2
  r=$(timeout "$TMO" "$SOLVER" "$b1$b2" "$CAP" 2>/dev/null)
  states=$(printf '%s' "$r" | sed -n 's/.*states \([0-9]*\).*/\1/p')
  case "$r" in
    *"PC POSSIBLE"*) echo "$b1 $b2 OK $states" ;;
    *"INCONCLUSIVE"*) echo "$b1 $b2 CAP $states" ;;
    "") echo "$b1 $b2 TIMEOUT -" ;;
    *) echo "$b1 $b2 FAIL $states" ;;
  esac
}
export -f resolve_one

# 이미 확정된 케이스를 제외한 목록을 만든다 (재개)
todo=$(mktemp)
while read -r b1 b2; do
  [ -z "${b1:-}" ] && continue
  if grep -q "^$b1 $b2 " "$out" 2>/dev/null; then
    continue
  fi
  echo "$b1 $b2"
done < "$cases" > "$todo"

echo "남은 케이스 $(grep -c . "$todo") / 전체 $(grep -c . "$cases")"
xargs -a "$todo" -n 2 -P "$par" bash -c 'resolve_one "$0" "$1"' >> "$out"
rm -f "$todo"

echo "=== 집계 ==="
awk '{print $3}' "$out" | sort | uniq -c
