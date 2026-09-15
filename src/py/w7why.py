# w=7, R=4, T 단독에서 열 카운트 해마다 기하 실현을 전수로 시험한다 (배치 순서 x 가로 방향 선택 전부).
# 입력: 없음. 출력: 해별 "PC=True/False" 와 실제로 지운 줄 수.
# 열 카운팅이 통과시킨 해 중 어느 것이 실제 PC 가 되는지 가려내는 자리다.
import itertools
from functools import lru_cache

W = 7
HCAP = 10
TOTCLEAR = 4

# T orientations as (dr,dc) cell lists, normalized
T_UP    = [(0,0),(0,1),(0,2),(1,1)]   # profile (1,2,1)
T_DOWN  = [(0,1),(1,0),(1,1),(1,2)]   # profile (1,2,1)
T_P     = [(1,0),(0,1),(1,1),(2,1)]   # profile (1,3)  nub left
T_Q     = [(0,0),(1,0),(2,0),(1,1)]   # profile (3,1)  nub right

LABEL = {'H': [T_UP, T_DOWN], 'P': [T_P], 'Q': [T_Q]}

def rowsof(board):
    return board

def drop(board, cells, col):
    """board: tuple of HCAP row-bitmasks. returns (newboard, ncleared) or None"""
    r = HCAP
    def hits(rr0):
        for dr, dc in cells:
            rr = rr0 + dr
            cc = col + dc
            if rr >= HCAP:
                continue
            if board[rr] >> cc & 1:
                return True
        return False
    while r > 0 and not hits(r-1):
        r -= 1
    nb = list(board)
    for dr, dc in cells:
        rr = r + dr
        if rr >= HCAP:
            return None
        nb[rr] |= 1 << (col + dc)
    full = (1 << W) - 1
    kept = [x for x in nb if x != full]
    nc = HCAP - len(kept)
    kept = kept + [0]*nc
    return (tuple(kept), nc)

def height(board):
    h = 0
    for i, x in enumerate(board):
        if x:
            h = i+1
    return h

def try_solution(placements):
    """placements: list of (label, startcol). try every order and orientation choice."""
    n = len(placements)
    best = [0]
    seen = set()
    def rec(board, remaining, clears):
        key = (board, remaining)
        if key in seen:
            return False
        seen.add(key)
        if not remaining:
            if board == tuple([0]*HCAP):
                return True
            return False
        for i in list(remaining):
            lb, col = placements[i]
            for cells in LABEL[lb]:
                res = drop(board, cells, col)
                if res is None:
                    continue
                nb, nc = res
                tc = clears + nc
                if tc > TOTCLEAR:
                    continue
                if height(nb) > TOTCLEAR - tc:
                    continue
                best[0] = max(best[0], tc)
                if rec(nb, remaining - {i}, tc):
                    return True
        return False
    ok = rec(tuple([0]*HCAP), frozenset(range(n)), 0)
    return ok, best[0]

SOLS = [
 [('P',0),('Q',0),('P',2),('Q',2),('H',4),('Q',4),('P',5)],
 [('P',0),('Q',0),('H',2),('Q',2),('P',3),('P',5),('Q',5)],
 [('P',0),('Q',0),('H',2),('Q',2),('H',3),('H',4),('P',5)],
 [('H',0),('Q',0),('P',1),('P',3),('Q',3),('P',5),('Q',5)],
 [('H',0),('Q',0),('P',1),('H',3),('Q',3),('H',4),('P',5)],
 [('H',0),('Q',0),('H',1),('P',2),('H',4),('Q',4),('P',5)],
 [('H',0),('Q',0),('H',1),('H',2),('P',3),('P',5),('Q',5)],
 [('H',0),('Q',0),('H',1),('H',2),('H',3),('H',4),('P',5)],
]

print("w=7, R=4, T only — each column-count solution tested for geometric realizability")
print("(every ordering x every H orientation choice)")
print()
for idx, s in enumerate(SOLS):
    nh = sum(1 for lb,_ in s if lb == 'H')
    ok, best = try_solution(s)
    desc = " ".join("%s@%d" % (lb,c) for lb,c in s)
    print("sol %d  horiz=%d  | %-34s | PC=%-5s  max rows cleared = %d / %d"
          % (idx+1, nh, desc, ok, best, TOTCLEAR))
