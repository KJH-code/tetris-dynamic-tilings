# 한 조각 종류의 열 카운트 해들을 뽑아 각각이 기하적으로 실현되는지 시험한다 (정리 4 의 하한 대조용).
# 입력: argv[1] = 폭 (기본 7), 그 외는 파일 안의 PIECE, R, NODE_CAP, NTRY.
# 출력: 열 해의 개수와, 앞 NTRY 개 중 실현 가능한 것의 배치 순서. 상한에 걸린 건수는 결론이 아니다.
import itertools, sys

W = int(sys.argv[1]) if len(sys.argv) > 1 else 7
R = int(sys.argv[2]) if len(sys.argv) > 2 else 8
NTRY = int(sys.argv[3]) if len(sys.argv) > 3 else 40
PIECE = sys.argv[4] if len(sys.argv) > 4 else 'J'

N = R * W // 4
TOTCLEAR = R
HCAP = R + 4

# cells per profile, normalized (dr, dc), dr upward from landing row
CELLS = {
 'J': {'B': [(0,2),(1,0),(1,1),(1,2)],
       'P': [(0,0),(0,1),(1,1),(2,1)],
       'A': [(0,0),(0,1),(0,2),(1,0)],
       'Q': [(0,0),(1,0),(2,0),(2,1)]},
 'L': {'B': [(0,0),(0,1),(0,2),(1,2)],
       'P': [(0,1),(1,1),(2,0),(2,1)],
       'A': [(0,0),(1,0),(1,1),(1,2)],
       'Q': [(0,0),(0,1),(1,0),(2,0)]},
}[PIECE]

PROF = {'A': (2,1,1), 'B': (1,1,2), 'P': (1,3), 'Q': (3,1)}

def colsolutions(w, R, limit=100000):
    out = []
    states = [((0,0), [])]
    items = list(PROF.items())
    for c in range(w):
        usable = [(lb,p) for lb,p in items if c + len(p) <= w]
        nxt = []
        for carry, hist in states:
            need = R - carry[0]
            if need < 0: continue
            for combo in itertools.product(*[range(0, need//p[0]+1) for lb,p in usable]):
                if sum(cnt*p[0] for cnt,(lb,p) in zip(combo,usable)) != need: continue
                nc = []
                for k in (1,2):
                    v = carry[k] if k < 2 else 0
                    for cnt,(lb,p) in zip(combo,usable):
                        if k < len(p): v += cnt*p[k]
                    nc.append(v)
                if any(v > R for v in nc): continue
                nxt.append((tuple(nc), hist + [(c,lb,cnt) for cnt,(lb,p) in zip(combo,usable) if cnt>0]))
        states = nxt
    for carry, hist in states:
        if carry == (0,0):
            out.append(hist)
            if len(out) >= limit: break
    return out

FULL = (1 << W) - 1

def drop(board, cells, col):
    r = HCAP
    def hits(r0):
        for dr, dc in cells:
            rr = r0 + dr
            if rr >= HCAP: continue
            if board[rr] >> (col+dc) & 1: return True
        return False
    while r > 0 and not hits(r-1): r -= 1
    nb = list(board)
    for dr, dc in cells:
        if r + dr >= HCAP: return None
        nb[r+dr] |= 1 << (col+dc)
    kept = [x for x in nb if x != FULL]
    ncl = HCAP - len(kept)
    return (tuple(kept + [0]*ncl), ncl)

def height(board):
    h = 0
    for i, x in enumerate(board):
        if x: h = i+1
    return h

NODE_CAP = 400000

def realizable(placements):
    flat = []
    for c, lb, cnt in placements:
        for _ in range(cnt):
            flat.append((c, lb))
    n = len(flat)
    seen = set()
    nodes = [0]
    order = []
    def rec(board, rem, clears):
        nodes[0] += 1
        if nodes[0] > NODE_CAP: return None
        key = (board, rem)
        if key in seen: return False
        seen.add(key)
        if not rem:
            return board == tuple([0]*HCAP)
        capped = False
        for i in rem:
            col, lb = flat[i]
            res = drop(board, CELLS[lb], col)
            if res is None: continue
            nb, ncl = res
            tc = clears + ncl
            if tc > TOTCLEAR: continue
            if height(nb) > TOTCLEAR - tc: continue
            order.append((lb, col))
            r = rec(nb, rem - {i}, tc)
            if r: return True
            order.pop()
            if r is None: capped = True
        if capped: return None
        return False
    res = rec(tuple([0]*HCAP), frozenset(range(n)), 0)
    return res, order, nodes[0]

sols = colsolutions(W, R)
print("piece=%s  w=%d  R=%d  n=%d  |  column solutions: %d" % (PIECE, W, R, N, len(sols)))
print("testing first %d for geometric realizability (node cap %d each)" % (NTRY, NODE_CAP))
print()
capped = 0
for idx, s in enumerate(sols[:NTRY]):
    ok, order, nodes = realizable(s)
    desc = " ".join("%s@%d^%d" % (l,c,k) for c,l,k in s)
    if ok:
        print("*** REALIZABLE ***  solution %d: %s" % (idx+1, desc))
        print("    play order: " + "  ".join("%s@%d" % (l,c) for l,c in order))
        break
    if ok is None:
        capped += 1
else:
    print("none of the first %d realizable  (%d hit the node cap -> inconclusive)" % (NTRY, capped))
