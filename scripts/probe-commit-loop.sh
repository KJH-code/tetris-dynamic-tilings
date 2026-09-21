#!/bin/bash
# 오래 도는 탐침의 출력 파일을 주기적으로 커밋·푸시한다.
# 사용법: ./scripts/probe-commit-loop.sh <커밋할 파일...> [주기초]
#         (주기초 기본 600. 환경변수 BRANCH 로 브랜치 지정)
#
# **컨테이너가 회수되면 남는 것은 커밋이 아니라 푸시된 것이다.** 그래서
# 매 주기 origin..HEAD 를 세어 밀린 것을 다시 민다 (2026-09-20 에 29 개가 밀렸다).
#
# 스윕의 커밋 루프와 동시에 돌 수 있어 git index.lock 이 겹칠 수 있다.
# 실패하면 다음 주기에 다시 하므로 그대로 두면 되지만, 커밋은 몇 번 재시도한다.
set -u

REPO=$(cd "$(dirname "$0")/.." && pwd)
BRANCH=${BRANCH:-claude/intelligent-bohr-ejzybx}

files=()
period=600
for a in "$@"; do
  case "$a" in
    [0-9]*) period=$a ;;
    *) files+=("$a") ;;
  esac
done
[ ${#files[@]} -eq 0 ] && { echo "커밋할 파일을 주라."; exit 1; }

cd "$REPO"
while true; do
  if [ -n "$(git status --porcelain "${files[@]}" 2>/dev/null)" ]; then
    n=$(awk '!/^#/' "${files[0]}" 2>/dev/null | grep -c . || true)
    for i in 1 2 3; do
      git add "${files[@]}" 2>/dev/null && \
      git commit -q -m "data: I-first probe at ${n:-?} cases

A probe, not an exhaustive run: only the six prefixes that have
produced failures so far are attached, so zero failures here means
no counterexample among those prefixes, not a theorem.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0118FaHdVwXoMn8JUHikzaeY" && break
      sleep $((5 * i))
    done
  fi
  behind=$(git log --oneline "origin/$BRANCH..HEAD" 2>/dev/null | wc -l)
  if [ "$behind" -gt 0 ]; then
    pushed=no
    for i in 1 2 3 4 5; do git push -q origin "$BRANCH" 2>/dev/null && { pushed=yes; break; }; sleep $((2 ** i)); done
    echo "$(date +%H:%M) 밀린 $behind 개 push=$pushed"
  fi
  sleep "$period"
done
