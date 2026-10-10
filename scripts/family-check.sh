#!/bin/bash
# 가족 경계 전수 스윕의 한 번 점검 — 지킴이 Routine 이 매시 이걸 부른다.
#
#   ./scripts/family-check.sh
#
# 하는 일: (1) 탐침이 죽어 있으면 되살린다  (2) 대조군을 **이름으로** 확인한다
# (3) 검정 중인 규칙에 어긋나는 줄을 찾는다  (4) 결과를 커밋·푸시한다  (5) 한 줄 보고.
#
# 왜 스크립트인가: 점검 로직을 Routine 프롬프트에 적어두면 프롬프트가 낡는다.
# 2026-09 탐침에서 제외 목록이 프롬프트와 실행 블록 사이에서 어긋난 적이 있다.
set -u
cd "$(dirname "$0")/.." || exit 1

BR=claude/intelligent-bohr-ejzybx
CASES=data/family-cases.txt
OUT=data/family.out
PAR=${PAR:-4}

# (1) 탐침 되살리기. 결론(OK/FAIL)만 건너뛰므로 재시작이 안전하다.
if [ "$(ps -C ifirst-probe.sh -o pid= | wc -l)" -eq 0 ]; then
  nohup env PAR="$PAR" TMO=5400 ./scripts/ifirst-probe.sh "$CASES" "$OUT" \
    >> /tmp/family-probe.log 2>&1 &
  # 일꾼이 실제로 떴는지 확인한다 (빈 입력이면 안 뜨는 게 정상 — 아래에서 남은 수로 가린다)
  for _ in $(seq 24); do
    [ "$(ps -C fix4 -o pid= | wc -l)" -ge 1 ] && break
    sleep 5
  done
fi

# (2) 대조군 — 알려진 FAIL 이고 상태 수까지 안다.
# **위치가 아니라 이름으로 찾는다.** 병렬 출력은 완료 순서라 위치가 안 맞는다.
# **"틀림" 과 "아직 안 돌음" 을 갈라야 한다.** 안 돈 것을 틀림으로 세면 새벽에 거짓 경보가 울린다.
ok=0; wrong=""; notyet=0
for c in "TJLISZO OJZS FAIL 36891439" \
         "JLTISZO JOZS FAIL 54310249" \
         "OTJLISZ JZOS FAIL 45479696" \
         "JTZOLSI OJZS FAIL 45696247"; do
  set -- $c
  line=$(awk -v a="$1" -v b="$2" '!/^#/ && $1==a && $2==b && ($3=="OK"||$3=="FAIL")' "$OUT" | tail -1)
  if [ -z "$line" ]; then notyet=$((notyet+1))
  elif [ "$line" = "$c" ]; then ok=$((ok+1))
  else wrong="$wrong\n  기대 [$c]  실제 [$line]"
  fi
done

# (3) 검정 중인 규칙: 블록 1(접두사가 {J,O,S,Z} 순열) 에서
#     PC 불가능 <=> S 가 마지막이고 J 가 Z 보다 앞.
#     어긋나는 줄은 도구 고장이 아니라 **발견**이다.
viol=$(awk '!/^#/ && NF>=3 && ($3=="OK" || $3=="FAIL") {
    b2=$2
    if (b2 !~ /^[JOSZ]{4}$/) next                     # 블록 1 만 본다
    sl = (substr(b2,4,1) == "S")
    jz = (index(b2,"J") < index(b2,"Z"))
    want = (sl && jz) ? "FAIL" : "OK"
    if ($3 != want) printf "%s %s %s (규칙예측 %s)\n", $1, $2, $3, want
  }' "$OUT")

# (4) 미결(CAP) 은 결론이 아니다 — 상한을 올려 다시 돌려야 한다.
cap=$(awk '!/^#/ && $3=="CAP"' "$OUT" | wc -l)

left=$(comm -13 <(awk '!/^#/ && NF>=3 && ($3=="OK"||$3=="FAIL") {print $1,$2}' "$OUT" | sort -u) \
                <(awk '!/^#/ && NF {print $1,$2}' "$CASES" | sort -u) | wc -l)
tot=$(awk '!/^#/ && NF' "$CASES" | wc -l)

# (5) 결과를 레포에 남긴다. 컨테이너에 남는 것은 커밋된 것이 아니라 **푸시된 것**이다.
pushed=""
if [ -n "$(git status --porcelain -- "$OUT")" ]; then
  git add "$OUT"
  git commit -q -m "data: family boundary sweep, $((tot-left))/$tot settled

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0118FaHdVwXoMn8JUHikzaeY"
fi
behind=$(git log --oneline "origin/$BR..HEAD" 2>/dev/null | wc -l)
if [ "$behind" -gt 0 ]; then
  for d in 0 2 4 8 16; do
    [ "$d" -gt 0 ] && sleep "$d"
    git push -q -u origin "$BR" 2>/dev/null && break
  done
  behind=$(git log --oneline "origin/$BR..HEAD" 2>/dev/null | wc -l)
  pushed="  미푸시 $behind"
fi

ctrl="대조군 $ok/4"
[ "$notyet" -gt 0 ] && ctrl="$ctrl (미계산 $notyet)"
echo "진행 $((tot-left))/$tot  남은 $left  fix4 $(ps -C fix4 -o pid= | wc -l)  $ctrl  미결 $cap$pushed"
if [ -n "$wrong" ]; then echo "대조군이 어긋났다 — 자료보다 검사 패턴을 먼저 의심할 것:"; printf "%b\n" "$wrong"; fi
if [ -n "$viol" ]; then echo "규칙에 어긋나는 줄:"; echo "$viol"; fi
[ "$left" -eq 0 ] && echo "스윕 완료 — 576 건 표가 닫혔다 (정리 H 확장 포함)"
exit 0
