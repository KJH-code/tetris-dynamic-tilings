#!/bin/bash
# 1,260 류 × 840 접두사 전수를 시작하거나 이어서 돌린다. 재시작 후 이 한 줄이면 된다.
# 사용법: ./scripts/sweep1260-run.sh [작업디렉터리]   (기본: $SCRATCH/sweep1260 또는 ./.sweep1260)
#
# 컨테이너가 회수되면 작업디렉터리는 사라지고 레포의 data/sweep1260/ 만 남는다.
# 그래서 맨 먼저 레포에서 작업디렉터리로 되돌린다 — 이걸 빼먹으면 끝난 류를 다시 돈다.
#
# 세 가지를 띄운다.
#   1 단계  bag1sweep.sh (상한 8M)         — 류마다 840 접두사
#   2 단계  미결을 큰 상한으로 확정         — 30 분마다 새 미결을 모아 돌린다
#   커밋    20 분마다 완료분을 레포로 옮겨 커밋·푸시
#
# **1 단계의 FAIL 0 은 결과가 아니다.** 실패는 2 단계에서만 드러난다.
# 2026-09-18 에 표본 100 개의 1 단계가 FAIL 0 을 냈는데 CAP 641 건 안에 실패 9 건이 있었다.
set -u

REPO=$(cd "$(dirname "$0")/.." && pwd)
WORK=${1:-${SCRATCH:-$REPO/.sweep1260}}
BRANCH=${BRANCH:-claude/intelligent-bohr-ejzybx}
PAR1=${PAR1:-3}   # 1 단계
PAR2=${PAR2:-1}   # 2 단계
mkdir -p "$WORK/sweep1260" "$REPO/data/sweep1260"

# --- 복구: 레포에 커밋된 완료분을 작업디렉터리로 되돌린다 ---
cp -n "$REPO/data/sweep1260"/*.out "$WORK/sweep1260/" 2>/dev/null
rm -f "$WORK/sweep1260"/*.partial
echo "복구: 완료 류 $(ls "$WORK/sweep1260"/*.out 2>/dev/null | wc -l) / 1260"

cd "$REPO"

# --- 1 단계 ---
nohup env PAR=$PAR1 ./scripts/bag1sweep.sh data/bag1-classes-1260.txt \
      data/bag2-prefixes.txt "$WORK/sweep1260" >> "$WORK/sweep1260.log" 2>&1 &
echo "1 단계 시작 (PAR=$PAR1)"

# --- 2 단계: 30 분마다 아직 확정 안 된 미결을 모아 돌린다 ---
nohup bash -c '
REPO='"$REPO"'; WORK='"$WORK"'; PAR2='"$PAR2"'
while true; do
  sleep 1800
  touch "$WORK/cap-resolved.out"
  # 아직 확정 안 된 미결만 추린다
  grep -H " CAP\| TIMEOUT" "$WORK"/sweep1260/*.out 2>/dev/null \
    | sed "s#.*/##; s#\.out:# #; s# \(CAP\|TIMEOUT\)\$##" \
    | while read -r b1 b2; do
        grep -q "^$b1 $b2 " "$WORK/cap-resolved.out" || echo "$b1 $b2"
      done > "$WORK/cap-todo.txt"
  n=$(grep -c . "$WORK/cap-todo.txt")
  [ "$n" -eq 0 ] && continue
  echo "$(date +%H:%M) 2 단계: 미결 $n 건"
  cd "$REPO" && PAR=$PAR2 TMO=3600 ./scripts/capresolve.sh "$WORK/cap-todo.txt" "$WORK/cap-resolved.out" >/dev/null 2>&1
done' >> "$WORK/stage2.log" 2>&1 &
echo "2 단계 루프 시작 (PAR=$PAR2, 30 분 주기)"

# --- 커밋: 20 분마다 ---
nohup bash -c '
REPO='"$REPO"'; WORK='"$WORK"'; BRANCH='"$BRANCH"'
while true; do
  cp -n "$WORK"/sweep1260/*.out "$REPO/data/sweep1260/" 2>/dev/null
  cd "$REPO"
  n=$(ls data/sweep1260/*.out 2>/dev/null | wc -l)
  if [ "$n" -gt 0 ]; then
    ok=$(cat data/sweep1260/*.out | grep -c " OK")
    fail=$(cat data/sweep1260/*.out | grep -c " FAIL")
    und=$(cat data/sweep1260/*.out | grep -cE " (CAP|TIMEOUT)")
    res=$(grep -c . "$WORK/cap-resolved.out" 2>/dev/null || echo 0)
    rfail=$(grep -c " FAIL " "$WORK/cap-resolved.out" 2>/dev/null || echo 0)
    {
      echo "# 1,260 류 × 840 접두사 전수 — 진행 중"
      echo "# 류 목록 data/bag1-classes-1260.txt (I 위치 내림차순, 어려운 쪽 먼저)"
      echo "# 이어서 돌리기: ./scripts/sweep1260-run.sh"
      echo "#"
      echo "# **1 단계의 FAIL 0 은 결과가 아니다.** 실패는 2 단계에서만 드러난다."
      echo "#"
      echo "완료 류          $n / 1260"
      echo "케이스           $((n*840))"
      echo "1 단계 OK        $ok"
      echo "1 단계 FAIL      $fail"
      echo "1 단계 미결      $und      <- 2 단계 대상"
      echo "2 단계 확정      $res      (그중 FAIL $rfail)"
      if [ "$fail" -gt 0 ]; then
        echo "#"; echo "# 1 단계에서 바로 드러난 실패"
        grep -H " FAIL" data/sweep1260/*.out | sed "s#data/sweep1260/##; s#\.out:# #; s# FAIL##"
      fi
    } > data/sweep1260-summary.out
    if [ -s "$WORK/cap-resolved.out" ]; then sort "$WORK/cap-resolved.out" > data/sweep1260-stage2.out; fi
  fi
  if [ -n "$(git status --porcelain data/sweep1260 data/sweep1260-summary.out data/sweep1260-stage2.out 2>/dev/null)" ]; then
    git add data/sweep1260 data/sweep1260-summary.out data/sweep1260-stage2.out 2>/dev/null
    git commit -q -m "data: 1260-class sweep at $n/1260 classes

Stage one: $ok possible, $fail impossible, $und undecided.
Stage two has settled $res of those, $rfail of them impossible.
An undecided case is neither a pass nor a failure until stage two
settles it.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0118FaHdVwXoMn8JUHikzaeY"
    for i in 1 2 3 4; do git push -q origin "$BRANCH" 2>/dev/null && break; sleep $((2**i)); done
    echo "$(date +%H:%M) committed $n classes, stage2 $res"
  fi
  sleep 1200
done' >> "$WORK/autocommit.log" 2>&1 &
echo "커밋 루프 시작 (20 분 주기)"
echo
echo "로그: $WORK/sweep1260.log  $WORK/stage2.log  $WORK/autocommit.log"
