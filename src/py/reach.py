#!/usr/bin/env python3
"""fix4.cpp 의 의미론을 그대로 옮긴 도달 상태 열거기 (증명용 구조 조사).

fix4 는 가능/불가능만 답한다. 사람 증명을 쓰려면 **어느 지점에서 도달 집합이
가장 좁은지** 와 **그 집합이 무엇인지** 를 봐야 하므로 전부 센다.

수 하나가 도착 하나를 정확히 소비하므로 **도착 인덱스 i 가 자연스러운 층**이다.
층 i 의 상태는 (보드, 홀드) 이고, 보조정리 1(스태시는 많아야 한 번)로
    placed = i - (홀드가 찼으면 1),
놓인 칸이 4*placed - 10*clears 이므로
    clears = (4*placed - popcount(board)) / 10
이다. 즉 placed 와 clears 가 (보드, i, 홀드) 의 함수다 — fix4 의 메모 키가 건전하다.

**fix4 와 맞춘 기록 (2026-10-08).** 짧은 수열을 주면 fix4 는 10 배치에 못 닿아
전체 도달 집합을 훑고 그 수를 그대로 보고한다. 그 값과 이 열거기의 층 합이

    TJLO    161,816     TJLOI   1,356,466     TJLOIS  6,472,372

로 **한 자리도 안 틀리고 같다.** fix4(2²⁷ 지문)·fix5(완전 128 비트 키) 에 이어
모델의 세 번째 독립 구현이다.

사용법: python3 -u reach.py <도착수열> [--boards <i>]
"""
import sys
from collections import defaultdict

W, HCAP, TOTCLEAR, TARGET = 10, 8, 4, 10
NAMES = "IOTSZJL"
BASECELL = [
    [0, 0, 0, 1, 0, 2, 0, 3], [0, 0, 0, 1, 1, 0, 1, 1], [0, 0, 0, 1, 0, 2, 1, 1],
    [0, 0, 0, 1, 1, 1, 1, 2], [0, 1, 0, 2, 1, 0, 1, 1], [0, 0, 0, 1, 0, 2, 1, 0],
    [0, 0, 0, 1, 0, 2, 1, 2],
]


def build():
    """fix4 의 buildorientations 와 같다 — 회전 (r,c) -> (c,-r), 정규화 후 중복제거."""
    oricell, oriwidth, bypiece = [], [], []
    for p in range(7):
        seen, cur, idxs = set(), list(BASECELL[p]), []
        for _ in range(4):
            minr = min(cur[2 * k] for k in range(4))
            minc = min(cur[2 * k + 1] for k in range(4))
            pts = sorted((cur[2 * k] - minr, cur[2 * k + 1] - minc) for k in range(4))
            key = tuple(x for pt in pts for x in pt)
            if key not in seen:
                seen.add(key)
                idxs.append(len(oricell))
                oricell.append(key)
                oriwidth.append(max(key[2 * k + 1] for k in range(4)) + 1)
            cur = [v for k in range(4) for v in (cur[2 * k + 1], -cur[2 * k])]
        bypiece.append(idxs)
    return oricell, oriwidth, bypiece


ORICELL, ORIWIDTH, BYPIECE = build()
FULL = (1 << W) - 1
EMPTY = 7          # 홀드가 빈 상태


def collides(b, oi, col, r):
    cells = ORICELL[oi]
    for k in range(4):
        rr, cc = r + cells[2 * k], col + cells[2 * k + 1]
        if rr >= HCAP:
            continue
        if (b >> (rr * W + cc)) & 1:
            return True
    return False


def clearlines(b):
    out, outrow, cnt = 0, 0, 0
    for r in range(HCAP):
        row = (b >> (r * W)) & FULL
        if row == FULL:
            cnt += 1
            continue
        out |= row << (outrow * W)
        outrow += 1
    return out, cnt


def heightof(b):
    for r in range(HCAP - 1, -1, -1):
        if (b >> (r * W)) & FULL:
            return r + 1
    return 0


def drops(b, piece, clears):
    """fix4 의 후보 생성과 같은 가지치기. (새보드, 새클리어수) 목록."""
    out = []
    for oi in BYPIECE[piece]:
        cells = ORICELL[oi]
        for col in range(W - ORIWIDTH[oi] + 1):
            r = HCAP
            while r > 0 and not collides(b, oi, col, r - 1):
                r -= 1
            b2, over = b, False
            for k in range(4):
                rr, cc = r + cells[2 * k], col + cells[2 * k + 1]
                if rr >= HCAP:
                    over = True
                    break
                b2 |= 1 << (rr * W + cc)
            if over:
                continue
            b2, cl = clearlines(b2)
            nc = clears + cl
            if nc > TOTCLEAR or heightof(b2) > TOTCLEAR - nc:
                continue
            out.append((b2, nc))
    return out


def placed_of(i, hold):
    return i - (0 if hold == EMPTY else 1)


def clears_of(board, placed):
    cells = 4 * placed - bin(board).count('1')
    assert cells >= 0 and cells % W == 0, (board, placed)
    return cells // W


def levels(seq):
    """층 i 의 상태 집합을 i = 0 … L 로 돌려준다. 상태는 (보드, 홀드)."""
    arr = [NAMES.index(ch) for ch in seq]
    L = len(arr)
    lv = [set() for _ in range(L + 1)]
    lv[0].add((0, EMPTY))
    for i in range(L):
        for (b, h) in lv[i]:
            placed = placed_of(i, h)
            if placed > TARGET:
                continue
            clears = clears_of(b, placed)
            a = arr[i]
            if h == EMPTY:                      # 스태시 — 아무것도 안 놓는다
                lv[i + 1].add((b, a))
            # 놓을 수 있는 것: 도착한 것(홀드 유지) 또는 홀드에 있던 것(도착이 홀드로)
            opts = [(a, h)] if h == EMPTY else [(a, h), (h, a)]
            for toplace, nhold in opts:
                if placed + 1 > TARGET:
                    continue
                for (b2, nc) in drops(b, toplace, clears):
                    lv[i + 1].add((b2, nhold))
    return lv, L


def report(seq, showboards=None):
    lv, L = levels(seq)
    print(f"수열 {seq}   L={L}, 목표 배치 {TARGET}")
    print(f"{'i':>3} {'상태':>9} {'보드':>8}   배치별 (클리어 분포)")
    for i in range(L + 1):
        bydepth = defaultdict(lambda: defaultdict(int))
        for (b, h) in lv[i]:
            p = placed_of(i, h)
            bydepth[p][clears_of(b, p)] += 1
        boards = {b for (b, _) in lv[i]}
        desc = "  ".join(
            f"p={p}[" + ",".join(f"c{c}:{n}" for c, n in sorted(d.items())) + "]"
            for p, d in sorted(bydepth.items()))
        print(f"{i:>3} {len(lv[i]):>9} {len(boards):>8}   {desc}")
    pc = [(b, h) for (b, h) in lv[L] if b == 0 and placed_of(L, h) == TARGET]
    print("PC 가능" if pc else "PC 불가능")
    if showboards is not None:
        i = showboards
        print(f"\n--- 층 i={i} 의 보드 (배치별)")
        bb = defaultdict(set)
        for (b, h) in lv[i]:
            bb[placed_of(i, h)].add(b)
        for p, s in sorted(bb.items()):
            print(f"  배치 {p}: 서로 다른 보드 {len(s)} 개")
    return lv, L


def show(b):
    hh = max(1, heightof(b))
    return "\n".join("".join('#' if (b >> (r * W + c)) & 1 else '.' for c in range(W))
                     for r in range(hh - 1, -1, -1))


if __name__ == '__main__':
    seq = sys.argv[1]
    sb = None
    if '--boards' in sys.argv:
        sb = int(sys.argv[sys.argv.index('--boards') + 1])
    report(seq, sb)
