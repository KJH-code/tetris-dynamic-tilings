#!/usr/bin/env python3
"""1,260 류 스윕의 실패를 집계한다 — 검산 대장의 재현 명령.

사용법: python3 scripts/failstats.py [2단계결과파일] [탐침결과파일]
        기본 data/sweep1260-stage2.out, data/probe954.out

**1 단계의 FAIL 0 은 결과가 아니다.** 실패는 2 단계 확정 파일에만 나온다.
그래서 이 스크립트는 2 단계 파일만 읽는다.

**스윕과 탐침은 서로 다른 모집단이다.** 스윕은 완료된 류에 접두사 840 개를 전수로
붙이고, 탐침은 나머지 류에 접두사 14 개만 붙인다. 그래서 위쪽 절은 스윕만 집계하고,
맨 아래 "스윕 ∪ 탐침" 절이 둘을 합집합으로 합쳐 **지금까지 알려진 실패 전체**를 준다.
비율은 어느 절에서 뽑은 것인지 반드시 같이 적을 것.

bag1 류 목록은 I 위치 내림차순이라 **완료된 부분은 무작위 표본이 아니다.**
비율을 뽑을 때는 어느 층(I 위치)이 끝났는지 먼저 볼 것 — 2026-09-19 에
"실패 0" 을 결과로 읽었다가 순서의 그림자였던 적이 있다.
"""
import sys
import os
import glob
from collections import Counter

stage2 = sys.argv[1] if len(sys.argv) > 1 else 'data/sweep1260-stage2.out'
probe = sys.argv[2] if len(sys.argv) > 2 else 'data/probe954.out'
classes = 'data/bag1-classes-1260.txt'
outdir = 'data/sweep1260'


def pos(b1, ch):
    return b1.index(ch) + 1


# 같은 케이스가 두 줄 이상 있을 수 있다 (2 단계가 겹쳐 돌면 생긴다 — 2026-09-21 에 1 건).
# **결론(OK/FAIL)이 미결(CAP/TIMEOUT)을 이긴다.** 나중 줄 우선으로 읽으면
# 먼저 나온 OK 를 TIMEOUT 이 덮어써 "아직 안 끝났다" 로 잘못 읽힌다.
RANK = {'OK': 2, 'FAIL': 2, 'CAP': 1, 'TIMEOUT': 1}
best = {}
for line in open(stage2):
    p = line.split()
    if len(p) < 3 or p[2] not in RANK:
        continue
    k = (p[0], p[1])
    old = best.get(k)
    if old and RANK[old[0]] == 2 and RANK[p[2]] == 2 and old[0] != p[2]:
        raise SystemExit(f"충돌: {k} 가 {old[0]} 이면서 {p[2]} 다")
    if old is None or RANK[p[2]] > RANK[old[0]]:
        best[k] = (p[2], p[3] if len(p) > 3 else '-')

fails = [(a, b, s) for (a, b), (v, s) in best.items() if v == 'FAIL']
undecided = [(a, b) for (a, b), (v, _) in best.items() if v in ('CAP', 'TIMEOUT')]

allc = [l.strip() for l in open(classes) if l.strip()]
done = sorted(os.path.basename(p)[:-4] for p in glob.glob(outdir + '/*.out'))
failcls = set(a for a, _, _ in fails)

print(f"완료 류 {len(done)} / {len(allc)}")
print(f"2 단계 실패 {len(fails)} 건 / {len(failcls)} 류, 미결 {len(undecided)} 건")
print()

print("접두사 분포")
for b2, n in sorted(Counter(b for _, b, _ in fails).items(), key=lambda x: (-x[1], x[0])):
    print(f"    {b2}  {n}")
print("  끝 글자 :", dict(sorted(Counter(b[-1] for _, b, _ in fails).items())))
print("  조각 집합:", dict(sorted(Counter(''.join(sorted(set(b))) for _, b, _ in fails).items())))
bad = [x for x in fails if set(x[1]) not in ({'O', 'S', 'Z', 'J'}, {'O', 'S', 'Z', 'L'})]
print("  {O,S,Z}+J/L 이 아닌 것:", bad if bad else "없음")
print()

print("I 위치별 (완료 류만)            류 / 실패 류")
for i in range(1, 8):
    d = [b for b in done if pos(b, 'I') == i]
    if not d:
        continue
    print(f"    I={i}   {len(d):4d} / {len([b for b in d if b in failcls]):3d}")
print("  I=2 인 류는 없다 — 정리 H 가 1·2 번째를 같은 류로 묶는다")
print()

print('"S·Z 가 둘 다 5 번째 이후" 조건 (2026-09-21 에 반증된 필요조건 후보)')
for name, sel in (("조건 만족", lambda b: min(pos(b, 'S'), pos(b, 'Z')) >= 5),
                  ("조건 위반", lambda b: min(pos(b, 'S'), pos(b, 'Z')) < 5)):
    a = [b for b in allc if sel(b)]
    d = [b for b in a if b in done]
    f = [b for b in d if b in failcls]
    ipos = sorted(set(pos(b, 'I') for b in d))
    print(f"    {name}: 전체 {len(a):4d}  완료 {len(d):4d}  실패 류 {len(f):3d}   완료분의 I 위치 {ipos}")
    if name == "조건 위반" and f:
        print("      반례:", [(b, f"I={pos(b,'I')}", f"S={pos(b,'S')}", f"Z={pos(b,'Z')}") for b in f])

if not os.path.exists(probe):
    sys.exit(0)

# 탐침은 접두사 14 개만 붙이므로 여기서 나온 "실패 0" 은 정리가 아니다.
# 반대로 FAIL 은 확정이다 — 그래서 합집합에 그대로 더할 수 있다.
pfail = {}
for line in open(probe):
    p = line.split()
    if len(p) >= 4 and p[2] == 'FAIL':
        pfail[(p[0], p[1])] = p[3]

states = {(a, b): s for (a, b), (v, s) in best.items() if v == 'FAIL'}
states.update(pfail)
union = sorted(states)

print()
print("스윕 ∪ 탐침 — 지금까지 알려진 실패 전체")
print(f"    스윕 {len(fails)} 건 / {len(failcls)} 류 (완료 류 {len(done)} 개 × 접두사 840 전수)")
print(f"    탐침 {len(pfail)} 건 / {len(set(a for a, _ in pfail))} 류 "
      f"(나머지 류 × 접두사 14 개만 — 전수가 아니다)")
print(f"    겹치는 케이스 {len(set(pfail) & set(k for k in best if best[k][0] == 'FAIL'))} 건 "
      f"(탐침 대조군)")
print(f"    합집합 **{len(union)} 건 / {len(set(a for a, _ in union))} 류**")
nums = sorted(int(s) for s in states.values() if s.isdigit())
print(f"    상태 수 {nums[0]:,} ~ {nums[-1]:,}")
print("    끝 글자 :", dict(sorted(Counter(b[-1] for _, b in union).items())))
print("    조각 집합:", dict(sorted(Counter(''.join(sorted(set(b))) for _, b in union).items())))
badu = [k for k in union if set(k[1]) not in ({'O', 'S', 'Z', 'J'}, {'O', 'S', 'Z', 'L'})]
print("    {O,S,Z}+J/L 이 아닌 것:", badu if badu else "없음")
print("    실패 bag1 의 I 위치:", dict(sorted(
    Counter(pos(a, 'I') for a in set(a for a, _ in union)).items())))
