import itertools

# ---- orientations, as (dr,dc) cell lists ----
# J base: (0,0),(0,1),(0,2),(1,0)   -> profile (2,1,1)
# L base: (0,0),(0,1),(0,2),(1,2)   -> profile (1,1,2)
def rotate(cells):
    out = [(c, -r) for r, c in cells]
    mr = min(r for r, c in out); mc = min(c for r, c in out)
    return sorted((r - mr, c - mc) for r, c in out)

def orientations(base):
    seen = {}
    cur = sorted(base)
    for _ in range(4):
        prof = []
        wid = max(c for r, c in cur) + 1
        for c in range(wid):
            prof.append(sum(1 for rr, cc in cur if cc == c))
        seen.setdefault(tuple(prof), []).append(list(cur))
        cur = rotate(cur)
    return seen

J = orientations([(0,0),(0,1),(0,2),(1,0)])
L = orientations([(0,0),(0,1),(0,2),(1,2)])

print("J profiles:", sorted(J.keys()))
print("L profiles:", sorted(L.keys()))
print("identical:", sorted(J.keys()) == sorted(L.keys()))
print()
for prof in sorted(J.keys()):
    print("profile %-10s  J cells %-34s  L cells %s" % (str(prof), str(J[prof][0]), str(L[prof][0])))
print()

# ---- column-count solutions ----
def colsolutions(profs, w, R, limit=10000):
    out = []
    states = [((0,0), [])]
    for c in range(w):
        usable = [p for p in profs if c + len(p) <= w]
        nxt = []
        for carry, hist in states:
            need = R - carry[0]
            if need < 0: continue
            for combo in itertools.product(*[range(0, need // p[0] + 1) for p in usable]):
                if sum(cnt*p[0] for cnt,p in zip(combo,usable)) != need: continue
                nc = []
                for k in (1,2):
                    v = carry[k] if k < 2 else 0
                    for cnt,p in zip(combo,usable):
                        if k < len(p): v += cnt*p[k]
                    nc.append(v)
                if any(v > R for v in nc): continue
                nxt.append((tuple(nc), hist + [(c,p,cnt) for cnt,p in zip(combo,usable) if cnt>0]))
        states = nxt
    for carry, hist in states:
        if carry == (0,0):
            out.append(hist)
            if len(out) >= limit: break
    return out

# ---- geometry ----
def realizable(placements, oridict, w, totclear, hcap=12):
    flat = []
    for c, prof, cnt in placements:
        for _ in range(cnt):
            flat.append((c, prof))
    n = len(flat)
    seen = set()
    def drop(board, cells, col):
        r = hcap
        def hits(r0):
            for dr, dc in cells:
                rr = r0 + dr
                if rr >= hcap: continue
                if board[rr] >> (col+dc) & 1: return True
            return False
        while r > 0 and not hits(r-1): r -= 1
        nb = list(board)
        for dr, dc in cells:
            if r+dr >= hcap: return None
            nb[r+dr] |= 1 << (col+dc)
        full = (1<<w)-1
        kept = [x for x in nb if x != full]
        ncl = hcap - len(kept)
        return (tuple(kept + [0]*ncl), ncl)
    def h(board):
        hh = 0
        for i,x in enumerate(board):
            if x: hh = i+1
        return hh
    def rec(board, rem, clears):
        if (board, rem) in seen: return False
        seen.add((board, rem))
        if not rem:
            return board == tuple([0]*hcap)
        for i in rem:
            col, prof = flat[i]
            for cells in oridict[prof]:
                res = drop(board, cells, col)
                if res is None: continue
                nb, ncl = res
                tc = clears + ncl
                if tc > totclear: continue
                if h(nb) > totclear - tc: continue
                if rec(nb, rem - {i}, tc): return True
        return False
    return rec(tuple([0]*hcap), frozenset(range(n)), 0)

profs = sorted(J.keys())
for w in [4, 5, 6]:
    for R in range(1, 9):
        if (R*w) % 4 != 0: continue
        n = R*w//4
        sols = colsolutions(profs, w, R)
        if not sols: continue
        jok = [s for s in sols if realizable(s, J, w, R)]
        lok = [s for s in sols if realizable(s, L, w, R)]
        print("w=%d R=%d n=%-2d | col solutions: %-3d | J realizes %-3d | L realizes %-3d %s"
              % (w, R, n, len(sols), len(jok), len(lok),
                 "  <-- DIVERGE" if (len(jok)>0) != (len(lok)>0) else ""))
        if (len(jok)>0) != (len(lok)>0):
            print("     solution(s) J can do but L cannot:")
            for s in jok:
                print("       " + "  ".join("%s@%d x%d" % (p,c,k) for c,p,k in s))
