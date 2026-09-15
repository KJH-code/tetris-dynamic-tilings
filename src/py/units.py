# Theorem 4: unit decomposition for J-only perfect clear.
# Verifies both halves of the proof, plus the full construction at all widths.
CELLS = {'A': [(0,0),(0,1),(0,2),(1,0)],   # profile (2,1,1)
         'B': [(0,2),(1,0),(1,1),(1,2)],   # profile (1,1,2)
         'P': [(0,0),(0,1),(1,1),(2,1)],   # profile (1,3)
         'Q': [(0,0),(1,0),(2,0),(2,1)]}   # profile (3,1)

UNIT5 = [('A',0),('P',1),('P',0),('P',3),('Q',0),('Q',3),('A',2),('A',0),('P',3),('B',1)]
UNITS = {'AB':    (4, 2, [('A',0),('B',1)]),
         'PQ':    (2, 4, [('P',0),('Q',0)]),
         'PQPQ':  (2, 8, [('P',0),('Q',0),('P',0),('Q',0)]),
         'UNIT5': (5, 8, UNIT5)}

def run(w, R, seq, clears_on):
    cap = R + 6; occ = set(); ncl = 0
    for lb, col in seq:
        cells = CELLS[lb]; r = cap
        while r > 0 and not any((r-1+dr, col+dc) in occ for dr, dc in cells): r -= 1
        new = {(r+dr, col+dc) for dr, dc in cells}
        if any(rr >= cap for rr, _ in new) or (new & occ): return None, None
        occ |= new
        if clears_on:
            fr = [rr for rr in range(cap) if all((rr,cc) in occ for cc in range(w))]
            if fr:
                fs = set(fr); ncl += len(fr)
                occ = {(rr - sum(1 for f in fr if f < rr), cc) for rr, cc in occ if rr not in fs}
    return occ, ncl

def construct(w):
    if w % 4 == 0:
        return [x for c in range(0, w, 4) for x in (('A',c),('B',c+1))], 2
    if w % 2 == 0:
        return [x for c in range(0, w, 2) for x in (('P',c),('Q',c))], 4
    seq = list(UNIT5)
    for c in range(5, w, 2):
        seq += [('P',c),('Q',c),('P',c),('Q',c)]
    return seq, 8

if __name__ == '__main__':
    print("(a) non-last unit: pure stacking fills rows 0..R-1 exactly")
    for nm,(w,R,seq) in UNITS.items():
        occ,_ = run(w,R,seq,False)
        tgt = {(r,c) for r in range(R) for c in range(w)}
        print("    %-6s %s" % (nm, "OK" if occ == tgt else "MISMATCH"))
    print("(b) last unit: with clears enabled, perfectly clears R rows")
    for nm,(w,R,seq) in UNITS.items():
        occ,ncl = run(w,R,seq,True)
        print("    %-6s %s" % (nm, "OK" if (not occ and ncl == R) else "MISMATCH"))
    print("full construction, widths 4..60")
    bad = 0
    for w in range(4,61):
        seq,R = construct(w)
        occ,ncl = run(w,R,seq,True)
        exp = w//2 if w%4==0 else (w if w%2==0 else 2*w)
        if occ or ncl != R or len(seq) != exp: bad += 1
    print("    failures:", bad)
