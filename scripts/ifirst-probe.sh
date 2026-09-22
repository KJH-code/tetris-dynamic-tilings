#!/bin/bash
# "I 가 맨 앞이면 항상 가능한가" 를 탐침한다.
# 사용법: ./scripts/ifirst-probe.sh <케이스파일> <출력파일>   (PAR, CAP, TMO 환경변수)
#
# 탐침이지 전수가 아니다. 840 접두사 전부가 아니라 **지금까지 실패를 낸 접두사** 만 붙인다.
# 그래서 "실패 0" 은 "반례가 이 접두사들에는 없다" 는 뜻이지 정리가 아니다.
#
# 이미 출력에 있는 케이스는 건너뛴다 (재개 가능). 컨테이너가 재시작되면 같은 줄을 다시 치면 된다:
#   nohup env PAR=1 ./scripts/ifirst-probe.sh $SCRATCH/ifirst-cases.txt $SCRATCH/ifirst-probe.out &
# 단 출력 파일이 작업디렉터리에만 있으면 재시작으로 사라진다 — 오래 돌릴 것은 레포에 커밋할 것.
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
  rc=$?
  states=$(printf '%s' "$r" | sed -n 's/.*states \([0-9]*\).*/\1/p')
  case "$r" in
    *"PC POSSIBLE"*)  echo "$b1 $b2 OK $states" ;;
    *"INCONCLUSIVE"*) echo "$b1 $b2 CAP $states" ;;
    "")
      # **빈 출력을 전부 TIMEOUT 으로 적으면 안 된다.** timeout 은 실제 시간 초과에
      # 124 를 주고, 그 밖의 0 아닌 값은 풀이가 **다른 이유로 죽은 것**이다.
      # 컨테이너 체크포인트가 자식만 죽이면 여기로 온다 — 2026-09-22 에 1 초면
      # 끝나는 케이스 세 건이 TIMEOUT 으로 기록됐다. 재시도 가능한 것으로 따로 적는다.
      if [ "$rc" -eq 124 ]; then echo "$b1 $b2 TIMEOUT -"; else echo "$b1 $b2 KILLED rc$rc"; fi ;;
    *)                echo "$b1 $b2 FAIL $states" ;;
  esac
}
export -f probe_one

todo=$(mktemp)
while read -r b1 b2; do
  [ -z "${b1:-}" ] && continue
  case "$b1" in '#'*) continue;; esac
  # **결론(OK/FAIL)만 건너뛴다.** CAP·TIMEOUT·KILLED 는 결론이 아니므로 다시 돈다 —
  # 옛 방식(줄이 있으면 건너뛰기)은 거짓 TIMEOUT 하나를 영구 미결로 굳혔다 (2026-09-22).
  grep -qE "^$b1 $b2 (OK|FAIL) " "$out" 2>/dev/null || echo "$b1 $b2"
done < "$cases" > "$todo"
echo "남은 $(grep -c . "$todo") / 전체 $(grep -c . "$cases")"

xargs -a "$todo" -n 2 -P "$par" bash -c 'probe_one "$0" "$1"' >> "$out"
rm -f "$todo"
echo "=== 집계 (머리 주석 제외) ==="
awk '!/^#/{print $3}' "$out" | sort | uniq -c
echo "=== FAIL 이 있으면 반례다 ==="
grep " FAIL " "$out" || echo "없음"
