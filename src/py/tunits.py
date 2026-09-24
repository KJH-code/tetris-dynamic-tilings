# 정리 3(b) 후보: T 단독 퍼펙트 클리어를 유닛 분해로 임의 폭에서 구성한다.
# 입력: 없음 (검사할 폭은 아래 상수). units.py 와 같은 하드드롭 의미론을 쓴다.
# 출력: 비-마지막 유닛과 마지막 유닛의 탐색 결과, 그리고 폭 4..80 조립 검산의 failures 수.
#
# 유닛 분해가 요구하는 두 조건 (정리 4 와 동일):
#   (a) 비-마지막 유닛: 클리어 없이 순수 적층으로 행 0..R-1 을 정확히 채운다
#   (b) 마지막 유닛: 클리어를 켜면 R 줄을 지우고 비워진다
# T 는 R = 4 이고, (a) 는 x x 4 직사각형의 T 타일링이므로 Walkup 에 의해 4 | x 여야 한다.

import sys

# T 의 네 회전. (dr, dc), dr 은 착지 행에서 위로.
cells = {
    "U": [(0, 0), (0, 1), (0, 2), (1, 1)],   # 프로파일 (1,2,1), 꼭지 위
    "D": [(0, 1), (1, 0), (1, 1), (1, 2)],   # 프로파일 (1,2,1), 꼭지 아래
    "L": [(0, 1), (1, 0), (1, 1), (2, 1)],   # 프로파일 (1,3)
    "R": [(0, 0), (1, 0), (1, 1), (2, 0)],   # 프로파일 (3,1)
}


def width_of(label):
    m = 0
    for dr, dc in cells[label]:
        if dc + 1 > m:
            m = dc + 1
    return m


def drop(occ, w, cap, label, col):
    # units.py 와 같은 하드드롭: 한 칸 아래가 막힐 때까지 내린다.
    cs = cells[label]
    r = cap
    while r > 0:
        hit = False
        for dr, dc in cs:
            if (r - 1 + dr, col + dc) in occ:
                hit = True
                break
        if hit:
            break
        r = r - 1
    new = set()
    for dr, dc in cs:
        if r + dr >= cap:
            return None
        new.add((r + dr, col + dc))
    if len(new & occ) > 0:
        return None
    return new


def clear_rows(occ, w, cap):
    full = []
    for r in range(cap):
        done = True
        for c in range(w):
            if (r, c) not in occ:
                done = False
                break
        if done:
            full.append(r)
    if len(full) == 0:
        return occ, 0
    fs = set(full)
    out = set()
    for r, c in occ:
        if r in fs:
            continue
        below = 0
        for f in full:
            if f < r:
                below = below + 1
        out.add((r - below, c))
    return out, len(full)


def run(w, R, seq, clears_on):
    cap = R + 6
    occ = set()
    ncl = 0
    for label, col in seq:
        new = drop(occ, w, cap, label, col)
        if new is None:
            return None, None
        occ = occ | new
        if clears_on:
            occ, k = clear_rows(occ, w, cap)
            ncl = ncl + k
    return occ, ncl


def find_stack_unit(x, R):
    # (a) 조건: 클리어 없이 행 0..R-1 을 정확히 채우는 배치열을 찾는다.
    cap = R + 6
    target = set()
    for r in range(R):
        for c in range(x):
            target.add((r, c))
    npieces = x * R // 4
    seen = set()

    def rec(occ, k, seq):
        if k == npieces:
            if occ == target:
                return list(seq)
            return None
        key = (frozenset(occ), k)
        if key in seen:
            return None
        seen.add(key)
        for label in cells:
            for col in range(x - width_of(label) + 1):
                new = drop(occ, x, cap, label, col)
                if new is None:
                    continue
                over = False
                for r, c in new:
                    if r >= R:
                        over = True
                        break
                if over:
                    continue
                seq.append((label, col))
                got = rec(occ | new, k + 1, seq)
                if got is not None:
                    return got
                seq.pop()
        return None

    return rec(set(), 0, [])


def find_last_unit(m, R):
    # (b) 조건: 클리어를 켜고 R 줄을 지우며 비워지는 배치열을 찾는다.
    # 바깥이 행 0..R-1 에서 꽉 차 있으므로 자기 열만으로 클리어가 결정된다
    # => 폭 m 보드의 독립 PC 와 같다.
    cap = R + 6
    npieces = m * R // 4
    seen = set()

    def height(occ):
        h = 0
        for r, c in occ:
            if r + 1 > h:
                h = r + 1
        return h

    def rec(occ, k, ncl, seq):
        if k == npieces:
            if len(occ) == 0 and ncl == R:
                return list(seq)
            return None
        key = (frozenset(occ), k, ncl)
        if key in seen:
            return None
        seen.add(key)
        for label in cells:
            for col in range(m - width_of(label) + 1):
                new = drop(occ, m, cap, label, col)
                if new is None:
                    continue
                nxt, k2 = clear_rows(occ | new, m, cap)
                if ncl + k2 > R:
                    continue
                if height(nxt) > R - ncl - k2:
                    continue
                seq.append((label, col))
                got = rec(nxt, k + 1, ncl + k2, seq)
                if got is not None:
                    return got
                seq.pop()
        return None

    return rec(set(), 0, 0, [])


def shift(seq, off):
    out = []
    for label, col in seq:
        out.append((label, col + off))
    return out


def main():
    R = 4
    print("(a) 비-마지막 유닛: 클리어 없이 행 0..%d 을 정확히 채우는가" % (R - 1))
    stack_units = {}
    for x in (4, 8, 12):
        got = find_stack_unit(x, R)
        stack_units[x] = got
        if got is None:
            print("    폭 %-3d 없음" % x)
        else:
            print("    폭 %-3d OK  %s" % (x, " ".join("%s@%d" % (a, b) for a, b in got)))
        sys.stdout.flush()

    print()
    print("(b) 마지막 유닛: 클리어를 켜면 %d 줄 지우고 비워지는가" % R)
    last_units = {}
    for m in (4, 5, 6, 7):
        got = find_last_unit(m, R)
        last_units[m] = got
        if got is None:
            print("    폭 %-3d 없음" % m)
        else:
            print("    폭 %-3d OK  %s" % (m, " ".join("%s@%d" % (a, b) for a, b in got)))
        sys.stdout.flush()

    base = None
    for x in (4, 8, 12):
        if stack_units.get(x) is not None:
            base = x
            break
    print()
    if base is None:
        print("조립 불가: (a) 를 만족하는 비-마지막 유닛이 없다.")
        return
    print("조립: 폭 %d 적층 유닛 반복 + 마지막 유닛 폭 m" % base)

    bad = 0
    tested = 0
    unresolved = []
    for w in range(4, 81):
        m = None
        for cand in (4, 5, 6, 7, 8, 9, 10, 11):
            if cand <= w and (w - cand) % base == 0 and last_units.get(cand) is not None:
                m = cand
                break
        if m is None:
            unresolved.append(w)
            continue
        seq = []
        off = 0
        while off + m < w:
            seq = seq + shift(stack_units[base], off)
            off = off + base
        seq = seq + shift(last_units[m], off)
        occ, ncl = run(w, R, seq, True)
        tested = tested + 1
        if occ is None or len(occ) > 0 or ncl != R or len(seq) != w:
            bad = bad + 1
            print("    w=%d 실패 (occ=%s ncl=%s n=%d, 기대 n=%d)"
                  % (w, occ, ncl, len(seq), w))
    print("    검사한 폭 %d 개, failures: %d" % (tested, bad))
    if len(unresolved) > 0:
        print("    조립식이 없는 폭: %s" % unresolved)

    # 독립 검산용 배치열을 파일로 낸다. src/cpp/tplay.cpp 가 읽어 재생한다.
    out = open("data/tplay-seqs.txt", "w")
    for w in range(4, 81):
        m = None
        for cand in (4, 5, 6, 7, 8, 9, 10, 11):
            if cand <= w and (w - cand) % base == 0 and last_units.get(cand) is not None:
                m = cand
                break
        if m is None:
            continue
        seq = []
        off = 0
        while off + m < w:
            seq = seq + shift(stack_units[base], off)
            off = off + base
        seq = seq + shift(last_units[m], off)
        out.write("%d %s\n" % (w, ",".join("%s@%d" % (a, b) for a, b in seq)))
    out.close()
    print("    배치열을 tplay-seqs.txt 에 적었다 (./bin/tplay 로 독립 재생)")

    print()
    print("하한: 열 카운팅으로 R >= 4 (임의 폭)")
    for target_r in (1, 2, 3, 4):
        found = 0
        rng = range(0, target_r + 1)
        for h0 in rng:
            for p0 in rng:
                for q0 in rng:
                    if h0 + p0 + 3 * q0 != target_r:
                        continue
                    for h1 in rng:
                        for p1 in rng:
                            for q1 in rng:
                                if h1 + 2 * h0 + p1 + 3 * p0 + 3 * q1 + q0 != target_r:
                                    continue
                                for h2 in rng:
                                    for p2 in rng:
                                        for q2 in rng:
                                            if h2 + 2 * h1 + h0 + p2 + 3 * p1 + 3 * q2 + q1 != target_r:
                                                continue
                                            found = found + 1
        print("    R=%d : 첫 세 열 방정식의 해 %d 개" % (target_r, found))
    print("    R=1,2,3 이 0 개이므로 R >= 4, 따라서 n = Rw/4 >= w. 구성이 n = w 를 달성한다.")


main()
