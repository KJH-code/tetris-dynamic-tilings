import itertools, sys
from functools import lru_cache

# column profiles per piece (contribution to consecutive columns)
PROFILES = {
    'I': [(1,1,1,1),(4,)],
    'O': [(2,2)],
    'T': [(1,2,1),(1,3),(3,1)],
    'S': [(1,2,1),(2,2)],
    'Z': [(1,2,1),(2,2)],
    'J': [(2,1,1),(1,1,2),(1,3),(3,1)],
    'L': [(1,1,2),(2,1,1),(3,1),(1,3)],
}

def feasible(profs, w, R):
    """Is there a nonneg integer placement multiset whose column totals are all exactly R?"""
    maxlen = max(len(p) for p in profs)
    carrylen = maxlen - 1
    start = tuple([0]*carrylen)
    states = {start}
    for c in range(w):
        usable = [p for p in profs if c + len(p) <= w]
        nxt = set()
        for st in states:
            cur = st[0] if carrylen > 0 else 0
            need = R - cur
            if need < 0:
                continue
            # enumerate counts for each usable profile
            ranges = [range(0, need // p[0] + 1) for p in usable]
            for combo in itertools.product(*ranges):
                if sum(cnt * p[0] for cnt, p in zip(combo, usable)) != need:
                    continue
                newc = []
                for k in range(1, carrylen + 1):
                    v = st[k] if k < carrylen else 0
                    for cnt, p in zip(combo, usable):
                        if k < len(p):
                            v += cnt * p[k]
                    newc.append(v)
                # prune: anything already exceeding R is dead
                if any(v > R for v in newc):
                    continue
                nxt.add(tuple(newc))
        states = nxt
        if not states:
            return False
    return tuple([0]*carrylen) in states

def minimal_R(profs, w, cap=60):
    for R in range(1, cap + 1):
        if feasible(profs, w, R):
            return R
    return None

print("minimal R (= total rows cleared) admitting a column-count solution")
print("R = None  ->  no solution for any R <= cap  ->  PERFECT CLEAR IMPOSSIBLE")
print()
widths = [4,5,6,7,8,9,10,11,12]
print("piece | " + " | ".join("w=%-2d" % w for w in widths))
print("-" * 70)
for name in "IOTSZJL":
    row = []
    for w in widths:
        R = minimal_R(PROFILES[name], w)
        if R is None:
            row.append(" -  ")
        else:
            n = R * w // 4
            if R * w % 4 != 0:
                row.append("R%-2d!" % R)
            else:
                row.append("R%-2d " % R)
    print("  %s   | " % name + " | ".join(row))
print()
print("cell-count consistency: R*w must be divisible by 4 (n = R*w/4 pieces)")
print()
for name in "IOTSZJL":
    out = []
    for w in widths:
        R = minimal_R(PROFILES[name], w)
        if R is None:
            out.append("%d:-" % w)
        else:
            out.append("%d:n=%s" % (w, (R*w)//4 if (R*w) % 4 == 0 else "?"))
    print("  %s  " % name + "  ".join(out))
