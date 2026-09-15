# 정리 4 의 홀수 폭 J 구성(UNIT5 + PQPQ)을 명시적으로 생성해 폭별로 재생한다.
# 입력: 없음 (파일 안의 홀수 폭 목록). 출력: 블록·꼬리·정리 배치 설명과 "w pieces rows-cleared PC?" 표.
# 배치 규칙이 폭에 의존하지 않는다는 것을 보이는 자리다.
import sys

# J orientations by column profile
CELLS = {'B': [(0,2),(1,0),(1,1),(1,2)],   # (1,1,2)
         'P': [(0,0),(0,1),(1,1),(2,1)],   # (1,3)
         'A': [(0,0),(0,1),(0,2),(1,0)],   # (2,1,1)
         'Q': [(0,0),(1,0),(2,0),(2,1)]}   # (3,1)

def run(w, seq, hcap, verbose=False):
    full = (1 << w) - 1
    board = [0]*hcap
    clears = 0
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
            if r + dr >= hcap: return None, clears
            board[r+dr] |= 1 << (col+dc)
        kept = [x for x in board if x != full]
        ncl = hcap - len(kept)
        clears += ncl
        board = kept + [0]*ncl
        if verbose:
            print("  %s@%-2d clear %d" % (lb, col, ncl))
    return (all(x == 0 for x in board)), clears

def construction(w):
    """odd w >= 5 : (w-3)/2 blocks of PPQQ, then the width-5 tail"""
    blocks = list(range(0, w-4, 2))          # 0, 2, ..., w-5
    t = w - 3                                 # tail start column
    seq = []
    for c in blocks:
        seq += [('P', c), ('P', c), ('Q', c)]
    seq += [('P', t+1), ('B', t), ('P', t), ('P', t+1), ('Q', t)]
    for c in blocks:
        seq += [('Q', c)]
    seq += [('Q', t)]
    return seq

print("J-only perfect clear, odd widths, explicit construction")
print("blocks: P@c,P@c,Q@c for c = 0,2,...,w-5   tail: P@(w-2),B@(w-3),P@(w-3),P@(w-2),Q@(w-3)")
print("cleanup: Q@c for each block, then Q@(w-3)")
print()
print(" w   pieces  rows cleared   PC?")
for w in range(5, 42, 2):
    seq = construction(w)
    n = len(seq)
    ok, cl = run(w, seq, 4*n//w + 4)
    print("%3d  %5d   %6s        %s" % (w, n, cl, "YES" if ok else ("no" if ok is not None else "overflow")))
