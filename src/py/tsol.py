import itertools

# T profiles: horizontal (1,2,1), vertical-nub-left (1,3), vertical-nub-right (3,1)
# label them H, P, Q
PROFS = [('H',(1,2,1)), ('P',(1,3)), ('Q',(3,1))]

def solutions(w, R, limit=200):
    """all nonneg integer placements whose column totals are exactly R everywhere"""
    out = []
    carrylen = 2
    # state: (carry tuple, list of (col, label, count))
    states = [((0,0), [])]
    for c in range(w):
        usable = [(lb,p) for lb,p in PROFS if c + len(p) <= w]
        nxt = []
        for carry, hist in states:
            need = R - carry[0]
            if need < 0:
                continue
            ranges = [range(0, need // p[0] + 1) for lb,p in usable]
            for combo in itertools.product(*ranges):
                if sum(cnt*p[0] for cnt,(lb,p) in zip(combo, usable)) != need:
                    continue
                nc = []
                for k in (1,2):
                    v = carry[k] if k < carrylen else 0
                    for cnt,(lb,p) in zip(combo, usable):
                        if k < len(p):
                            v += cnt*p[k]
                    nc.append(v)
                if any(v > R for v in nc):
                    continue
                nh = hist + [(c,lb,cnt) for cnt,(lb,p) in zip(combo,usable) if cnt>0]
                nxt.append((tuple(nc), nh))
            if len(nxt) > 50000:
                break
        states = nxt
    for carry, hist in states:
        if carry == (0,0):
            out.append(hist)
            if len(out) >= limit:
                break
    return out

for w, R in [(7,4), (9,4), (5,4), (4,4)]:
    sols = solutions(w, R)
    n = R*w//4
    print("=" * 62)
    print("w=%d  R=%d  ->  n=%d pieces   |  solutions found: %d" % (w, R, n, len(sols)))
    for s in sols[:12]:
        tot = sum(cnt for _,_,cnt in s)
        nh = sum(cnt for _,lb,cnt in s if lb=='H')
        desc = "  ".join("%s@%d x%d" % (lb,c,cnt) for c,lb,cnt in s)
        print("   n=%2d  horiz=%d  |  %s" % (tot, nh, desc))
    if len(sols) > 12:
        print("   ... (%d more)" % (len(sols)-12))
    # how many solutions use zero horizontal T?
    if sols:
        zeroh = [s for s in sols if not any(lb=='H' and cnt>0 for _,lb,cnt in s)]
        print("   solutions with NO horizontal T: %d / %d" % (len(zeroh), len(sols)))
