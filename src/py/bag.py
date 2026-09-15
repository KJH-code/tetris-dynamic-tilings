import itertools, sys
from functools import lru_cache

NAMES = "IOTSZJL"
def rot(cells):
    o=[(c,-r) for r,c in cells]
    mr=min(r for r,c in o); mc=min(c for r,c in o)
    return sorted((r-mr,c-mc) for r,c in o)
BASE={'I':[(0,0),(0,1),(0,2),(0,3)],'O':[(0,0),(0,1),(1,0),(1,1)],
      'T':[(0,0),(0,1),(0,2),(1,1)],'S':[(0,0),(0,1),(1,1),(1,2)],
      'Z':[(0,1),(0,2),(1,0),(1,1)],'J':[(0,0),(0,1),(0,2),(1,0)],
      'L':[(0,0),(0,1),(0,2),(1,2)]}
ORI={}
for p,b in BASE.items():
    cur=sorted(b); seen=set(); lst=[]
    for _ in range(4):
        k=tuple(cur)
        if k not in seen:
            seen.add(k); lst.append((cur, max(c for r,c in cur)+1))
        cur=rot(cur)
    ORI[p]=lst

def pc_possible(w, counts, cap=None):
    """counts: dict type->count. free ordering, hard drop. returns True/False"""
    n=sum(counts.values())
    if (4*n) % w: return False
    R=4*n//w
    if cap is None: cap=R+4
    full=(1<<w)-1
    seen=set()
    def rec(board, cnt, clears):
        key=(board,cnt)
        if key in seen: return False
        seen.add(key)
        if sum(cnt)==0:
            return all(x==0 for x in board)
        for idx,p in enumerate(NAMES):
            if cnt[idx]==0: continue
            nc=list(cnt); nc[idx]-=1; nc=tuple(nc)
            for cells,cw in ORI[p]:
                for col in range(w-cw+1):
                    r=cap
                    while r>0:
                        bad=False
                        for dr,dc in cells:
                            rr=r-1+dr
                            if rr<cap and (board[rr]>>(col+dc))&1: bad=True; break
                        if bad: break
                        r-=1
                    nb=list(board); over=False
                    for dr,dc in cells:
                        rr=r+dr
                        if rr>=cap: over=True; break
                        nb[rr]|=1<<(col+dc)
                    if over: continue
                    kept=[x for x in nb if x!=full]
                    ncl=cap-len(kept)
                    kept=tuple(kept+[0]*ncl)
                    tc=clears+ncl
                    if tc>R: continue
                    h=0
                    for i,x in enumerate(kept):
                        if x: h=i+1
                    if h>R-tc: continue
                    if rec(kept,nc,tc): return True
        return False
    return rec(tuple([0]*cap), tuple(counts.get(p,0) for p in NAMES), 0)

if __name__=='__main__':
    w=int(sys.argv[1]); mode=sys.argv[2]
    if mode=='n5':
        print("w=%d, n=5 : choose 5 distinct types from the first bag (2 rows)" % w)
        ok=[];no=[]
        for combo in itertools.combinations(NAMES,5):
            c={p:1 for p in combo}
            (ok if pc_possible(w,c) else no).append("".join(combo))
        print("  PC possible  (%d/%d): %s" % (len(ok),len(ok)+len(no), " ".join(ok)))
        print("  PC impossible(%d/%d): %s" % (len(no),len(ok)+len(no), " ".join(no)))
    elif mode=='n10':
        print("w=%d, n=10 : all 7 types once + 3 doubled types (4 rows)" % w)
        ok=[];no=[]
        for extra in itertools.combinations(NAMES,3):
            c={p:1 for p in NAMES}
            for p in extra: c[p]=2
            (ok if pc_possible(w,c) else no).append("".join(extra))
        print("  PC possible  (%d/35): %s" % (len(ok)," ".join(ok)))
        print("  PC impossible(%d/35): %s" % (len(no)," ".join(no)))
