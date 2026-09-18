#!/bin/bash
# bag1 표본마다 bag2 접두사 840 개를 훑어 7-bag 순서 제약의 실패를 찾는다.
# 사용법: ./scripts/bag1sweep.sh <bag1 목록 파일> <bag2 접두사 파일> <출력 디렉터리>
# 출력: <출력 디렉터리>/<bag1>.out, 한 줄 = "<접두사> OK|FAIL|CAP|TIMEOUT".
#
# **CAP 과 TIMEOUT 은 결론이 아니다.** 1 단계가 끝나면 그 케이스만 큰 상한으로 재실행해야 한다.
# 이미 완료된 bag1 은 건너뛰므로 중단 후 다시 돌리면 이어서 간다 (컨테이너 리셋 대비).
# 환경변수: SOLVER(기본 ./bin/fix4) CAP(8000000) TMO(60) PAR(3)
set -u

export SOLVER=${SOLVER:-./bin/fix4}
export CAP=${CAP:-8000000}
export TMO=${TMO:-60}
par=${PAR:-3}

list1=$1
list2=$2
outdir=$3
mkdir -p "$outdir"

run_one() {
  r=$(timeout "$TMO" "$SOLVER" "$1$2" "$CAP" 2>/dev/null)
  case "$r" in
    *"PC POSSIBLE"*) echo "$2 OK" ;;
    *"INCONCLUSIVE"*) echo "$2 CAP" ;;
    "") echo "$2 TIMEOUT" ;;
    *) echo "$2 FAIL" ;;
  esac
}
export -f run_one

while read -r b1; do
  [ -z "$b1" ] && continue
  out="$outdir/$b1.out"
  if [ -s "$out" ]; then
    continue
  fi
  tmp="$out.partial"
  : > "$tmp"
  xargs -a "$list2" -P "$par" -I{} bash -c 'run_one "$0" "$1"' "$b1" {} >> "$tmp"
  lines=$(grep -c . "$tmp")
  if [ "$lines" -ne 840 ]; then
    echo "WARN $b1 줄 수 $lines != 840 — 미완으로 두고 넘어간다"
    continue
  fi
  mv "$tmp" "$out"
  echo "done $b1 $(date +%H:%M:%S) $(awk '{print $2}' "$out" | sort | uniq -c | tr '\n' ' ')"
done < "$list1"
