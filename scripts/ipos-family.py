#!/usr/bin/env python3
"""I 위치 주장 두 개의 재현 — 검산 대장용.

  (1) 닫힌 가족:  bag1 = perm(T,J,L,O) + "ISZ",  bag2 in {JOZS, JZOS, OJZS}
                  -> 72 건 전부 불가능인가?
  (2) "I 를 한 칸 앞으로 당기면 손해가 아니다" 가 거짓인가?
                  w x y z S I Z  (I 6 번째)  vs  w x y z I S Z  (I 5 번째)

사용법: python3 scripts/ipos-family.py [2단계결과파일 ...]
        기본 data/sweep1260-stage2.out  data/resolved-extra.out

뒤에 오는 파일이 앞을 덮는다. `data/resolved-extra.out` 은 2 단계에서도
TIMEOUT 으로 남은 것을 더 긴 시간으로 따로 확정한 줄이다 — 2 단계 파일에는
옛 TIMEOUT 줄이 그대로 남아 있으므로 **덮어쓰는 순서가 중요하다.**

**대칭으로 접을 때 bag2 도 같이 바꿔야 한다.** 거울(J<->L, S<->Z)은 두 가방 모두에
작용하고, 홀드 교환(정리 H)은 bag1 의 앞 두 자리에만 작용한다. bag1 만 정규화하면
엉뚱한 줄을 읽는다.

1 단계의 OK 는 결론으로 쓴다 — OK 는 증인이 있다는 뜻이라 상한과 무관하게 참이다.
1 단계의 FAIL 0 은 결론이 아니므로 FAIL 은 2 단계 파일에서만 읽는다.
"""
import sys
import glob
import os
from itertools import permutations

MIRROR = str.maketrans('JLSZ', 'LJZS')


def mirror(s):
    return s.translate(MIRROR)


def hold_swap(b1):
    return b1[1] + b1[0] + b1[2:]


def canon(b1, b2):
    """(bag1, bag2) 의 궤도에서 사전 최소. 거울은 양쪽에, 교환은 bag1 에만."""
    return min([(b1, b2),
                (hold_swap(b1), b2),
                (mirror(b1), mirror(b2)),
                (mirror(hold_swap(b1)), mirror(b2))])


# 같은 케이스가 두 줄 이상 있을 수 있다 (2 단계가 겹쳐 돌면 생긴다 — 2026-09-21 에 1 건).
# **결론(OK/FAIL)이 미결(CAP/TIMEOUT)을 이긴다.** 나중 줄이 이기게 하면
# 먼저 나온 OK 를 TIMEOUT 이 덮어써서 "아직 안 끝났다" 로 읽힌다.
# OK 와 FAIL 이 충돌하면 그건 조용히 넘길 일이 아니라 즉시 멈출 일이다.
RANK = {'OK': 2, 'FAIL': 2, 'CAP': 1, 'TIMEOUT': 1}


def load(stage2files):
    verd = {}
    for path in stage2files:
        if not os.path.exists(path):
            continue
        for line in open(path):
            p = line.split()
            if len(p) >= 3 and p[2] in RANK:
                k = (p[0], p[1])
                old = verd.get(k)
                if old and RANK[old] == 2 and RANK[p[2]] == 2 and old != p[2]:
                    raise SystemExit(f"충돌: {k} 가 {old} 이면서 {p[2]} 다 ({path})")
                if old is None or RANK[p[2]] > RANK[old]:
                    verd[k] = p[2]
    for f in glob.glob('data/sweep1260/*.out'):        # 1 단계의 OK 만 보탠다
        b1 = os.path.basename(f)[:-4]
        for line in open(f):
            p = line.split()
            if len(p) >= 2 and p[1] == 'OK':
                verd.setdefault((b1, p[0]), 'OK')
    return verd


def main():
    files = sys.argv[1:] or ['data/sweep1260-stage2.out', 'data/resolved-extra.out']
    verd = load(files)
    look = lambda b1, b2: verd.get(canon(b1, b2), '?')
    probes = ('JOZS', 'JZOS', 'OJZS')

    print('(1) bag1 = perm(T,J,L,O) + "ISZ"  x  {JOZS, JZOS, OJZS}')
    counts = {}
    for pm in permutations('TJLO'):
        b1 = ''.join(pm) + 'ISZ'
        for b2 in probes:
            v = look(b1, b2)
            counts[v] = counts.get(v, 0) + 1
            if v != 'FAIL':
                print(f"    {b1} {b2}  ->  {v}")
    print(f"    72 건 중 {counts}")
    print(f"    주장(전부 불가능) {'성립' if counts.get('FAIL') == 72 else '미확정 또는 반례 있음'}")
    print()

    print('(2) I 를 6 번째에서 5 번째로 당기면? (S 와 자리 바꾸기)')
    flip = same_fail = same_ok = other = 0
    for pm in permutations('TJLO'):
        base = ''.join(pm)
        for b2 in probes:
            v6 = look(base + 'SIZ', b2)      # I 6 번째
            v5 = look(base + 'ISZ', b2)      # I 5 번째
            if v6 == 'OK' and v5 == 'FAIL':
                flip += 1
            elif v6 == 'FAIL' and v5 == 'FAIL':
                same_fail += 1
            elif v6 == 'OK' and v5 == 'OK':
                same_ok += 1
            else:
                other += 1
                print(f"    {base}SIZ/{base}ISZ {b2}  ->  {v6} / {v5}")
    print(f"    72 쌍: 당겼더니 불가능 {flip}, 양쪽 불가능 {same_fail}, "
          f"양쪽 가능 {same_ok}, 그 밖 {other}")
    print(f"    주장(\"앞으로 당기면 손해가 아니다\") {'거짓' if flip else '반례 없음'}")


main()
