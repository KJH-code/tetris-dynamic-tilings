# 동적 T-패리티 항등식(A)을 퍼펙트 클리어 수열 전수로 검증한다. verify.cpp 의 독립 구현.
# 입력: 인자로 "w n" 쌍들 (없으면 가벼운 7 케이스). `--shard=s/m` 을 주면 루트 분할 실행.
# 출력: 케이스별 PC 수열 개수와 네 항목의 실패 건수. verify.cpp 와 개수까지 일치해야 한다.
#
# 독립성을 위해 verify.cpp 와 다르게 구현한 지점:
#   - 보드를 __int128 비트마스크가 아니라 행별 정수 마스크의 튜플로 든다
#   - 착지 행을 충돌 탐침(한 칸씩 내려보기)이 아니라 **열 높이 프로파일 산술**로 구한다
#     (테트로미노는 각 열에서 칸이 연속이므로 r = max(colheight[c] - bottom[c]) 가 정확하다)
#   - D 를 "줄별 합" 이 아니라 **"자기 아래 지워진 줄 수가 홀수인 칸의 개수"** 로 센다.
#     두 정의가 mod 2 로 같다는 것도 같이 검사한다 (마지막 열).
import os
import sys

names = "IOTSZJL"
base = {
    "I": [(0, 0), (0, 1), (0, 2), (0, 3)],
    "O": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "T": [(0, 0), (0, 1), (0, 2), (1, 1)],
    "S": [(0, 0), (0, 1), (1, 1), (1, 2)],
    "Z": [(0, 1), (0, 2), (1, 0), (1, 1)],
    "J": [(0, 0), (0, 1), (0, 2), (1, 0)],
    "L": [(0, 0), (0, 1), (0, 2), (1, 2)],
}


def normalize(cells):
    mr = min(r for r, c in cells)
    mc = min(c for r, c in cells)
    return tuple(sorted((r - mr, c - mc) for r, c in cells))


def rotations(cells):
    out = []
    cur = normalize(cells)
    for _ in range(4):
        if cur not in out:
            out.append(cur)
        # verify.cpp 와 반대 방향으로 돈다: (r,c) -> (-c, r)
        cur = normalize([(-c, r) for r, c in cur])
    return out


def build():
    # (조각 이름, 셀, 폭, 열별 최하단 오프셋)
    out = []
    for nm in names:
        for cells in rotations(base[nm]):
            width = max(c for r, c in cells) + 1
            bottom = {}
            for r, c in cells:
                if c not in bottom or r < bottom[c]:
                    bottom[c] = r
            out.append((nm, cells, width, bottom))
    return out


pieces = build()


def heights(board, w, hcap):
    h = [0] * w
    for r in range(hcap):
        row = board[r]
        if row == 0:
            continue
        for c in range(w):
            if row >> c & 1:
                h[c] = r + 1
    return h


def place(board, w, hcap, cells, width, bottom, col):
    # 착지 행을 열 높이 프로파일로 직접 계산한다 (충돌 탐침을 쓰지 않는다).
    h = heights(board, w, hcap)
    r = 0
    for dc in range(width):
        need = h[col + dc] - bottom[dc]
        if need > r:
            r = need
    out = list(board)
    for dr, dc in cells:
        rr = r + dr
        if rr >= hcap:
            return None
        if out[rr] >> (col + dc) & 1:
            return None
        out[rr] |= 1 << (col + dc)
    return tuple(out)


def phi(board, w, hcap):
    s = 0
    for r in range(hcap):
        row = board[r]
        if row == 0:
            continue
        for c in range(w):
            if row >> c & 1:
                if (r + c) % 2 == 0:
                    s = s + 1
                else:
                    s = s - 1
    return s


def full_rows(board, w, hcap):
    mask = (1 << w) - 1
    out = []
    for r in range(hcap):
        if board[r] == mask:
            out.append(r)
    return out


def apply_clears(board, w, hcap, rows):
    drop = set(rows)
    kept = []
    for r in range(hcap):
        if r not in drop:
            kept.append(board[r])
    while len(kept) < hcap:
        kept.append(0)
    return tuple(kept)


def clear_stats(board, w, hcap, rows):
    # D_mine  = 자기 아래 지워진 줄 수가 홀수인 (살아남는) 칸의 개수
    # D_rows  = 줄별 합. verify.cpp 의 정의 (지워진 줄마다 그 위의, 꽉 찬 줄이 아닌 칸 수)
    # a       = 지워진 줄들의 phi 합
    drop = set(rows)
    d_mine = 0
    d_rows = 0
    for r in range(hcap):
        if board[r] == 0:
            continue
        if r in drop:
            continue
        below = 0
        for j in rows:
            if j < r:
                below = below + 1
        if below == 0:
            continue
        cnt = 0
        for c in range(w):
            if board[r] >> c & 1:
                cnt = cnt + 1
        d_rows = d_rows + below * cnt
        if below % 2 == 1:
            d_mine = d_mine + cnt
    a = 0
    for j in rows:
        rowphi = 0
        for c in range(w):
            if (j + c) % 2 == 0:
                rowphi = rowphi + 1
            else:
                rowphi = rowphi - 1
        a = a + rowphi
    return d_mine, d_rows, a


def height_of(board, w, hcap):
    for r in range(hcap - 1, -1, -1):
        if board[r] != 0:
            return r + 1
    return 0


def run_case(w, n, shard=None):
    # shard = (s, m): 루트(첫 조각)의 배치 선택지를 m 등분해 s 번째만 내려간다.
    # 선택지 번호는 배치 가능 여부와 무관하게 매기므로 분할이 결정적이고 서로 겹치지 않는다.
    # 탐색 로직은 건드리지 않는다 — m 개 샤드의 개수를 더하면 통짜 실행과 같아야 한다.
    if (4 * n) % w != 0:
        return None
    totclear = 4 * n // w
    hcap = totclear + 4
    start = tuple([0] * hcap)
    stats = {"pc": 0, "event": 0, "glob": 0, "aodd": 0, "read": 0, "ddef": 0}

    def rec(board, k, clears, tcount, dphisum, dsum, asum):
        if k == n:
            if board != start:
                return
            stats["pc"] = stats["pc"] + 1
            # global : sum(dphi) == 2*#T (mod 4)
            if (dphisum - 2 * tcount) % 4 != 0:
                stats["glob"] = stats["glob"] + 1
            # readable : #T == sum(D) + sum(A)/2 (mod 2)
            if asum % 2 != 0:
                stats["aodd"] = stats["aodd"] + 1
            else:
                if (tcount - dsum - asum // 2) % 2 != 0:
                    stats["read"] = stats["read"] + 1
            return
        rootidx = -1
        for nm, cells, width, bottom in pieces:
            for col in range(w - width + 1):
                if k == 0 and shard is not None:
                    rootidx = rootidx + 1
                    if rootidx % shard[1] != shard[0]:
                        continue
                pre = place(board, w, hcap, cells, width, bottom, col)
                if pre is None:
                    continue
                rows = full_rows(pre, w, hcap)
                nc = clears + len(rows)
                if nc > totclear:
                    continue
                post = pre
                dphi = 0
                d_mine = 0
                a = 0
                if len(rows) > 0:
                    d_mine, d_rows, a = clear_stats(pre, w, hcap, rows)
                    post = apply_clears(pre, w, hcap, rows)
                    dphi = phi(post, w, hcap) - phi(pre, w, hcap)
                    # per-event : dphi == -2D - A (mod 4)
                    if (dphi + 2 * d_mine + a) % 4 != 0:
                        stats["event"] = stats["event"] + 1
                    # 두 D 정의가 mod 2 로 같은가
                    if (d_mine - d_rows) % 2 != 0:
                        stats["ddef"] = stats["ddef"] + 1
                if height_of(post, w, hcap) > totclear - nc:
                    continue
                nt = tcount
                if nm == "T":
                    nt = nt + 1
                rec(post, k + 1, nc, nt, dphisum + dphi, dsum + d_mine, asum + a)

    rec(start, 0, 0, 0, 0, 0, 0)
    return stats


def main():
    args = sys.argv[1:]
    shard = None
    rest = []
    for a in args:
        if a.startswith("--shard="):
            s, m = a.split("=", 1)[1].split("/")
            shard = (int(s), int(m))
            if not (0 <= shard[0] < shard[1]):
                print("--shard=s/m 은 0 <= s < m 이어야 한다")
                sys.exit(2)
        else:
            rest.append(a)
    args = rest
    cases = []
    if len(args) >= 2:
        for i in range(0, len(args) - 1, 2):
            cases.append((int(args[i]), int(args[i + 1])))
    else:
        cases = [(4, 2), (4, 3), (4, 4), (5, 5), (6, 3), (8, 2), (8, 4)]
    total = 0
    bad = 0
    tag = "" if shard is None else " [shard %d/%d]" % (shard[0], shard[1])
    for w, n in cases:
        st = run_case(w, n, shard)
        if st is None:
            print("w=%2d n=%2d | skip (4n 이 w 로 나눠지지 않음)" % (w, n))
            continue
        total = total + st["pc"]
        bad = bad + st["event"] + st["glob"] + st["aodd"] + st["read"] + st["ddef"]
        print("w=%2d n=%2d%s | PC: %6d | per-event fail: %d | global fail: %d | "
              "sum(A) odd: %d | readable fail: %d | D 두 정의 mod2 불일치: %d"
              % (w, n, tag, st["pc"], st["event"], st["glob"], st["aodd"],
                 st["read"], st["ddef"]))
        sys.stdout.flush()
    print("합계 PC 수열 %d 개, 실패 총 %d 건%s" % (total, bad, tag))


main()
