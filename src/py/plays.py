#!/usr/bin/env python3
"""배치열 집합 Plays_n(q) 의 두 독립 계산 — 정리 H 의 일반화를 검산한다.

fix4.cpp 의 규칙만 쓴다 (보드는 안 본다). 상태 = (도착 인덱스 i, 홀드 h).

    (S)  h = 없음 일 때만:  아무것도 안 놓고 q_i 를 홀드에
    (P0)                    q_i 를 놓는다 (홀드 유지)
    (P1) h != 없음 일 때만: 홀드를 놓고 q_i 를 홀드에

세 수 모두 도착을 정확히 하나 소비한다. 보드는 배치열이 정해지면 따라오므로
(7-bag.md §정리 H 의 모델 절), 배치열 집합만 비교하면 순서 효과를 다 본다.

구현 A: 위 세 규칙을 그대로 재귀.
구현 B: 사슬 특성화 —
    도착을 a_0 a_1 ... a_m 이라 하면(첫 도착이 (S) 로 홀드에 들어가 a_0 가 된다),
    "홀드를 뱉는" 단계들의 위치 j_1 < ... < j_r 이 사슬을 이루고,
    사슬 위치 j_k 에는 a_{j_{k-1}} 이 (j_0 = 0), 나머지 위치 j 에는 a_j 가 나온다.
    마지막 홀드는 a_{j_r} 이다.

사용법: python3 src/py/plays.py [최대 길이]
"""
import sys
from itertools import combinations, product

NONE = '.'


def plays_rules(q, n):
    """구현 A — 규칙 그대로."""
    out = set()

    def rec(i, h, placed):
        if len(placed) == n:
            out.add(''.join(placed))
            return
        if i >= len(q):
            return
        if h == NONE:
            rec(i + 1, q[i], placed)                 # (S)
        rec(i + 1, h, placed + [q[i]])               # (P0)
        if h != NONE:
            rec(i + 1, q[i], placed + [h])           # (P1)

    rec(0, NONE, [])
    return out


def plays_chain(q, n):
    """구현 B — 사슬 특성화. 첫 도착은 반드시 홀드로 간다고 놓는다(따름정리 H1)."""
    out = set()
    L = len(q)
    # (S) 를 k 번째에서 쓰는 플레이는 전부 k=0 으로 흡수된다 (보조정리 2).
    # 그래도 흡수를 가정하지 않고, 스태시 위치 k 를 전부 돌려서 A 와 맞는지 본다.
    for k in range(L):
        if k + 1 + n > L + 1:      # k 개 배치 + 스태시 1 + 남은 도착으로 n 개를 못 채우면 버린다
            continue
        head = list(q[:k])
        if len(head) > n:
            continue
        a = [q[k]] + list(q[k + 1:])          # a_0 = 스태시된 것, 그 뒤가 스트림
        m = n - len(head)                     # 홀드 게임이 내야 하는 개수
        if m < 0 or m > len(a) - 1:
            continue
        for r in range(m + 1):
            for chain in combinations(range(1, m + 1), r):
                res = [None] * (m + 1)        # 1..m 번 자리
                prev = 0
                for j in chain:
                    res[j] = a[prev]
                    prev = j
                for j in range(1, m + 1):
                    if res[j] is None:
                        res[j] = a[j]
                out.add(''.join(head + res[1:]))
    return out


def main():
    maxlen = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    alpha = 'abcdef'
    bad = 0
    checked = 0
    for L in range(2, maxlen + 1):
        for n in range(1, L):
            for q in product(alpha[:min(L, 4)], repeat=L):
                q = ''.join(q)
                A = plays_rules(q, n)
                B = plays_chain(q, n)
                checked += 1
                if A != B:
                    bad += 1
                    if bad <= 5:
                        print(f"  불일치 q={q} n={n}  A-B={sorted(A-B)[:4]}  B-A={sorted(B-A)[:4]}")
    print(f"구현 A vs 구현 B: {checked} 개 비교, 불일치 {bad}")

    # 정리 H: 첫 두 자리 교환은 Plays 를 보존한다 (L >= n+1 일 때)
    print()
    print("정리 H — q_0 <-> q_1 교환 (L >= n+1)")
    bad0 = tot0 = 0
    for L in range(2, maxlen + 1):
        for n in range(1, L):
            for q in product(alpha[:4], repeat=L):
                q = ''.join(q)
                sw = q[1] + q[0] + q[2:]
                tot0 += 1
                if plays_rules(q, n) != plays_rules(sw, n):
                    bad0 += 1
                    if bad0 <= 3:
                        print(f"  반례 q={q} n={n} L-n={L-n}")
    print(f"  {tot0} 쌍 중 반례 {bad0}   (L >= n+1 이 아닌 경우 포함)")

    # i >= 1 인 인접 교환은 보존하지 않는다 — 가장 짧은 반례를 찾는다
    print()
    print("인접 교환 q_i <-> q_{i+1}, i >= 1 — 가장 짧은 반례")
    found = None
    for L in range(3, maxlen + 1):
        for n in range(1, L):
            if L < n + 1:
                continue
            for q in product(alpha[:3], repeat=L):
                q = ''.join(q)
                for i in range(1, L - 1):
                    sw = q[:i] + q[i + 1] + q[i] + q[i + 2:]
                    A, B = plays_rules(q, n), plays_rules(sw, n)
                    if A != B:
                        found = (q, sw, i, n, L, sorted(A - B), sorted(B - A))
                        break
                if found:
                    break
            if found:
                break
        if found:
            break
    if found:
        q, sw, i, n, L, ab, ba = found
        print(f"  q={q} -> {sw}  (i={i}, n={n}, L={L},  L-n={L-n})")
        print(f"  q 만 되는 배치열 : {ab}")
        print(f"  교환본만 되는 것 : {ba}")
    else:
        print("  반례 없음 (탐색 범위 안에서)")


main()
