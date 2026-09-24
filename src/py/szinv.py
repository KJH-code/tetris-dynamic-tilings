# 정리 5 의 불변량 I0~I3 를 2 열 블록의 도달 가능 상태 전부에서 검사한다.
# 입력: 인자로 높이 캡 H 들 (없으면 12 14 16 18). szlang.py 와 독립 구현이라 상태 수 교차검증도 된다.
# 출력: H 별 "states" 개수와 I0..I3 위반 건수. 위반이 하나라도 있으면 종료 코드 1.
import sys

# 세로 Z : 왼쪽 열 {r, r+1}, 오른쪽 열 {r+1, r+2}
# 세로 S : 왼쪽 열 {r+1, r+2}, 오른쪽 열 {r, r+1}
vert = {"Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
        "S": [(1, 0), (2, 0), (0, 1), (1, 1)]}


def collides(rows, cells, r, h):
    for dr, dc in cells:
        rr = r + dr
        if rr >= h:
            continue
        if rows[rr] >> dc & 1:
            return True
    return False


def place(rows, cells, h):
    # (L2) 한 칸 아래로 못 내려가는 가장 낮은 자리. 하드드롭 경로는 쓰지 않는다.
    r = h
    while r > 0 and not collides(rows, cells, r - 1, h):
        r = r - 1
    out = list(rows)
    for dr, dc in cells:
        if r + dr >= h:
            return None
        out[r + dr] |= 1 << dc
    return tuple(out)


def clear_options(rows, h):
    # 블록 안에서 두 열이 다 찬 줄(값 3)만 클리어 후보다. 그런데 보드 전체의 줄이
    # 꽉 차려면 다른 블록들도 그 줄이 꽉 차야 하므로, 이 블록만 보면 후보의
    # 어떤 부분집합이든 실제로 지워질 수 있다. 그래서 부분집합 전부를 전개한다.
    # 실제 도달 집합의 **과대근사**이고, 불가능성 증명에는 과대근사가 안전하다.
    full = []
    for i in range(h):
        if rows[i] == 3:
            full.append(i)
    out = []
    for mask in range(1, 1 << len(full)):
        drop = set()
        for k in range(len(full)):
            if mask >> k & 1:
                drop.add(full[k])
        kept = []
        for i in range(h):
            if i not in drop:
                kept.append(rows[i])
        out.append(tuple(kept + [0] * len(drop)))
    return out


def reach(h):
    start = tuple([0] * h)
    seen = set([start])
    frontier = [start]
    while len(frontier) > 0:
        nxt = []
        for st in frontier:
            for name in vert:
                p = place(st, vert[name], h)
                if p is None:
                    continue
                for q in [p] + clear_options(p, h):
                    if q not in seen:
                        seen.add(q)
                        nxt.append(q)
        frontier = nxt
    return seen


def violations(st, h):
    bad = []
    f0 = []
    f1 = []
    for r in range(h):
        if st[r] & 1:
            f0.append(r)
        if st[r] >> 1 & 1:
            f1.append(r)
    # I0. |F0| = |F1|
    if len(f0) != len(f1):
        bad.append("I0")
    # I1. 내부에 빈 줄이 없다 (비지 않은 줄이 0 부터 연속)
    occupied = []
    for r in range(h):
        if st[r] != 0:
            occupied.append(r)
    if len(occupied) > 0 and occupied != list(range(len(occupied))):
        bad.append("I1")
    # I2. |d_j| <= 1
    n0 = 0
    n1 = 0
    for j in range(h):
        if st[j] & 1:
            n0 = n0 + 1
        if st[j] >> 1 & 1:
            n1 = n1 + 1
        if abs(n0 - n1) > 1:
            bad.append("I2")
            break
    # I3. 보드가 비지 않으면 d_0 != 0 (= 행 0 이 꽉 차지 않는다)
    if len(occupied) > 0:
        d0 = (st[0] & 1) - (st[0] >> 1 & 1)
        if d0 == 0:
            bad.append("I3")
    return bad


def main():
    heights = [int(x) for x in sys.argv[1:]]
    if len(heights) == 0:
        heights = [12, 14, 16, 18]
    worst = 0
    for h in heights:
        states = reach(h)
        count = {"I0": 0, "I1": 0, "I2": 0, "I3": 0}
        for st in states:
            for name in violations(st, h):
                count[name] = count[name] + 1
        total = count["I0"] + count["I1"] + count["I2"] + count["I3"]
        worst = worst + total
        print("   H=%-3d %6d states   I0 %d  I1 %d  I2 %d  I3 %d   violations %d"
              % (h, len(states), count["I0"], count["I1"], count["I2"],
                 count["I3"], total))
    if worst > 0:
        print("   INVARIANT VIOLATED")
        sys.exit(1)
    print("   all invariants hold")


main()
