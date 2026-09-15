# 정리 5 의 핵심 질문을 2 열 블록 완화에서 직접 묻는다: 블록의 행 0 이 꽉 찰 수 있는가 (= I3).
# 입력: argv[1] = 높이 캡 H (기본 14). 출력: 도달 상태 수와 행 0 이 꽉 찬 상태의 개수 (0 이어야 한다).
# szinv.py 와 같은 결론을 다른 코드로 확인하는 자리다.
import itertools, sys

H = int(sys.argv[1]) if len(sys.argv) > 1 else 14

# vertical pieces confined to a 2-wide block, cells (dr, dc)
# vertical Z : col0 rows r,r+1 ; col1 rows r+1,r+2
# vertical S : col0 rows r+1,r+2 ; col1 rows r,r+1
VERT = {
    'Z': [(0,0),(1,0),(1,1),(2,1)],
    'S': [(1,0),(2,0),(0,1),(1,1)],
}
# for comparison
EXTRA = {
    'O': [(0,0),(0,1),(1,0),(1,1)],
}

def place(rows, cells):
    """rows: tuple of H bitmasks over 2 columns. gravity drop, return new rows or None"""
    r = H
    def hits(r0):
        for dr, dc in cells:
            rr = r0 + dr
            if rr >= H: continue
            if rows[rr] >> dc & 1: return True
        return False
    while r > 0 and not hits(r-1): r -= 1
    nb = list(rows)
    for dr, dc in cells:
        if r + dr >= H: return None
        nb[r+dr] |= 1 << dc
    return tuple(nb)

def clears(rows):
    """all results of clearing a nonempty subset of locally-full rows"""
    full = [i for i,x in enumerate(rows) if x == 3]
    out = []
    for k in range(1, len(full)+1):
        for sub in itertools.combinations(full, k):
            ss = set(sub)
            kept = [x for i,x in enumerate(rows) if i not in ss]
            out.append(tuple(kept + [0]*len(ss)))
    return out

def explore(pieces, label):
    start = tuple([0]*H)
    seen = {start}
    frontier = [start]
    hit = None
    depth = 0
    while frontier and depth < 60:
        nxt = []
        for st in frontier:
            for nm in pieces:
                p = place(st, pieces[nm])
                if p is None: continue
                cands = [p] + clears(p)
                for q in cands:
                    if q in seen: continue
                    seen.add(q)
                    if q[0] == 3:            # row 0 completely full
                        hit = (nm, depth+1)
                    nxt.append(q)
        frontier = nxt
        depth += 1
        if hit: break
    return hit, len(seen), depth

print("2-column block relaxation, height cap H = %d" % H)
print("question: can row 0 of a block ever become completely full?")
print()
for pieces, label in [({'Z':VERT['Z']}, "vertical S only  (mirror of Z-only)"),
                      (VERT, "vertical S and Z  <-- the {S,Z} case"),
                      (dict(list(VERT.items()) + list(EXTRA.items())), "S, Z and O  (control: should be YES)"),
                      (EXTRA, "O only  (control: should be YES)")]:
    hit, nstates, d = explore(pieces, label)
    print("  %-38s -> %s   (%d states explored, depth %d)"
          % (label, ("ROW 0 FULL REACHABLE" if hit else "row 0 NEVER full"), nstates, d))
