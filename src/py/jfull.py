import sys
CELLS = {'B': [(0,2),(1,0),(1,1),(1,2)],
         'P': [(0,0),(0,1),(1,1),(2,1)],
         'A': [(0,0),(0,1),(0,2),(1,0)],
         'Q': [(0,0),(1,0),(2,0),(2,1)]}

def run(w, seq, hcap):
    full = (1 << w) - 1
    board = [0]*hcap
    for (lb, col) in seq:
        cells = CELLS[lb]
        r = hcap
        def hits(r0):
            for dr, dc in cells:
                rr = r0 + dr
                if rr >= hcap: continue
                if board[rr] >> (col+dc) & 1: return True
            return False
        while r > 0 and not hits(r-1): r -= 1
        for dr, dc in cells:
            if r + dr >= hcap: return None
            board[r+dr] |= 1 << (col+dc)
        kept = [x for x in board if x != full]
        ncl = hcap - len(kept)
        board = kept + [0]*ncl
    return all(x == 0 for x in board)

def construct(w):
    if w % 2 == 0:
        # PQ blocks: 2 columns each, R = 4
        seq = []
        for c in range(0, w, 2):
            seq += [('P', c), ('Q', c)]
        return seq, 4
    blocks = list(range(0, w-4, 2))
    t = w - 3
    seq = []
    for c in blocks:
        seq += [('P', c), ('P', c), ('Q', c)]
    seq += [('P', t+1), ('B', t), ('P', t), ('P', t+1), ('Q', t)]
    for c in blocks:
        seq += [('Q', c)]
    seq += [('Q', t)]
    return seq, 8

print(" w    n     R    PC?")
bad = 0
for w in range(4, 61):
    seq, R = construct(w)
    n = len(seq)
    ok = run(w, seq, R + 4)
    if not ok: bad += 1
    print("%3d %4d %5d    %s" % (w, n, R, "YES" if ok else "FAIL"))
print()
print("failures:", bad)

