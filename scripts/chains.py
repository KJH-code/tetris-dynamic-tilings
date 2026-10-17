#!/usr/bin/env python3
"""보조정리 P 의 사슬을 돌려 "I 가 맨 앞" 케이스에서 어떤 플레이가 통하는지 센다.

보조정리 P: 홀드를 뱉는 자리 집합 C = {j_1 < … < j_r} 하나가 플레이 하나다.
따름정리 H1 로 a_0 을 처음부터 홀드에 넣어도 손해가 없으므로, 도착을
a_0 (홀드) + 스트림 a_1 … a_m 으로 본다. 그러면 배치열은

    자리 j_k  ->  a_{j_{k-1}}   (j_0 = 0)
    사슬 밖 j ->  a_j
    끝에 홀드에 남는 것 = a_{j_r}  (r = 0 이면 a_0)

배치열이 정해지면 홀드 없는 고정순서 문제가 되므로 `bin/seq` 로 판정한다.
"""
import subprocess
import sys
from itertools import combinations


def order_of(arr, C):
    """arr = a_0 … a_m. C 는 1..m 안의 자리 집합. 배치열(길이 m)을 돌려준다."""
    m = len(arr) - 1
    out, prev = [], 0            # prev = 현재 홀드에 있는 것의 인덱스
    for j in range(1, m + 1):
        if j in C:
            out.append(arr[prev])
            prev = j
        else:
            out.append(arr[j])
    return ''.join(out), arr[prev]


def seq_ok(order, w=10, timeout=120):
    r = subprocess.run(['./bin/seq', str(w), order],
                       capture_output=True, text=True, timeout=timeout)
    head = r.stdout.split('\n')[0]
    if 'PERFECT CLEAR FOUND' in head:
        return True
    if 'NO perfect clear' in head:
        return False
    raise SystemExit(f"판정 불명: {order} -> {head!r}")


def chains_upto(m, k):
    for r in range(k + 1):
        for C in combinations(range(1, m + 1), r):
            yield frozenset(C)


def main():
    seqs = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    maxsize = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    for s in seqs:
        arr = list(s)
        m = len(arr) - 1
        assert m == 10, f"{s}: 스트림 길이가 10 이어야 한다 (L=11)"
        good, tried = [], 0
        for C in chains_upto(m, maxsize):
            order, left = order_of(arr, C)
            tried += 1
            if seq_ok(order):
                good.append((sorted(C), order, left))
        tag = "통함" if good else "**|C|<=%d 에서 전멸**" % maxsize
        print(f"{s}  사슬 {tried} 개 시도, 통한 것 {len(good)} 개  {tag}")
        for C, order, left in good[:3]:
            print(f"      C={C}  배치열 {order}  (남는 것 {left})")
        sys.stdout.flush()


if __name__ == '__main__':
    main()
