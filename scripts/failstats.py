#!/usr/bin/env python3
"""1,260 류 스윕의 실패를 집계한다 — 검산 대장의 재현 명령.

사용법: python3 scripts/failstats.py [2단계결과파일]
        기본 data/sweep1260-stage2.out

**1 단계의 FAIL 0 은 결과가 아니다.** 실패는 2 단계 확정 파일에만 나온다.
그래서 이 스크립트는 2 단계 파일만 읽는다.

bag1 류 목록은 I 위치 내림차순이라 **완료된 부분은 무작위 표본이 아니다.**
비율을 뽑을 때는 어느 층(I 위치)이 끝났는지 먼저 볼 것 — 2026-09-19 에
"실패 0" 을 결과로 읽었다가 순서의 그림자였던 적이 있다.
"""
import sys
import os
import glob
from collections import Counter

stage2 = sys.argv[1] if len(sys.argv) > 1 else 'data/sweep1260-stage2.out'
classes = 'data/bag1-classes-1260.txt'
outdir = 'data/sweep1260'


def pos(b1, ch):
    return b1.index(ch) + 1


fails = []
undecided = []
for line in open(stage2):
    p = line.split()
    if len(p) < 3:
        continue
    if p[2] == 'FAIL':
        fails.append((p[0], p[1], p[3] if len(p) > 3 else '-'))
    elif p[2] in ('CAP', 'TIMEOUT'):
        undecided.append((p[0], p[1]))

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
