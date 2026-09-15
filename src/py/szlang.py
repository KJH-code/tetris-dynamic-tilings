import itertools
from collections import defaultdict

# 2-column block. Row labels: E(empty) A(col0 only) B(col1 only) F(full)
# vertical Z : col0 {r,r+1}, col1 {r+1,r+2}
# vertical S : col0 {r+1,r+2}, col1 {r,r+1}
VERT = {'Z': [(0,0),(1,0),(1,1),(2,1)], 'S': [(1,0),(2,0),(0,1),(1,1)]}
LAB = {0:'E', 1:'A', 2:'B', 3:'F'}

def reach(H):
    def place(rows, cells):
        r = H
        def hits(r0):
            for dr, dc in cells:
                rr = r0+dr
                if rr >= H: continue
                if rows[rr] >> dc & 1: return True
            return False
        while r > 0 and not hits(r-1): r -= 1
        nb = list(rows)
        for dr, dc in cells:
            if r+dr >= H: return None
            nb[r+dr] |= 1 << dc
        return tuple(nb)
    def clears(rows):
        full = [i for i,x in enumerate(rows) if x == 3]
        out = []
        for k in range(1, len(full)+1):
            for sub in itertools.combinations(full, k):
                ss = set(sub)
                kept = [x for i,x in enumerate(rows) if i not in ss]
                out.append(tuple(kept + [0]*len(ss)))
        return out
    start = tuple([0]*H); seen = {start}; fr = [start]
    while fr:
        nx = []
        for st in fr:
            for nm in VERT:
                p = place(st, VERT[nm])
                if p is None: continue
                for q in [p] + clears(p):
                    if q not in seen:
                        seen.add(q); nx.append(q)
        fr = nx
    return seen

def word(st):
    # strip trailing empties, read bottom-up
    top = 0
    for i,x in enumerate(st):
        if x: top = i+1
    return "".join(LAB[st[i]] for i in range(top))

for H in (12, 14, 16):
    S = reach(H)
    W = set(word(s) for s in S)
    print("H=%d : %d states, %d distinct words" % (H, len(S), len(W)))

H = 16
S = reach(H)
W = sorted(set(word(s) for s in S), key=lambda x: (len(x), x))
print()
print("shortest reachable words (bottom row first):")
for w in W[:26]:
    print("   " + (w if w else "(empty)"))
print()
# which letters can start a word?
starts = defaultdict(int)
for w in W:
    if w: starts[w[0]] += 1
print("first letter (row 0) distribution:", dict(starts))
print()
# Myhill-Nerode style: group words by their set of admissible continuations?
# simpler: check whether membership is determined by a bounded-window property.
# test: is the language closed under deleting an F?  (that is what a clear does)
bad = [w for w in W if any(w[i]=='F' and (w[:i]+w[i+1:]).rstrip('E') not in W for i in range(len(w)))]
print("words where deleting some F leaves the language:", len(bad))
if bad:
    for w in bad[:5]:
        for i in range(len(w)):
            if w[i]=='F' and (w[:i]+w[i+1:]).rstrip('E') not in W:
                print("   %s  --delete F at %d-->  %s   (NOT reachable)" % (w, i, (w[:i]+w[i+1:]).rstrip('E')))
                break
