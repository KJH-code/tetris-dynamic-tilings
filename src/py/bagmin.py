# 7-bag 제약 하의 최소 조각 수 표를 재현한다 (볼트 7-bag.md "최소 조각 수").
# 입력: 인자 없으면 폭 4..16 전부, 인자가 있으면 그 폭들만. 환경변수 MSET 으로 바이너리 경로 지정 가능.
# 출력: 폭마다 "w=10 unconstrained=5 sevenbag=10" 한 줄과, 시도한 n 별 가능/불가능 내역.
import itertools
import os
import subprocess
import sys

names = "IOTSZJL"
mset = os.environ.get("MSET", "./bin/mset")


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def bag_multisets(n):
    # 7-bag: 완전한 가방 q 개 + 부분 가방 s 개. 각 종류는 q 또는 q+1 개이고
    # q+1 인 종류가 정확히 s 개다. 가방 안 순열은 자유라고 보므로 multiset 만 남는다.
    q = n // 7
    s = n % 7
    out = []
    for extra in itertools.combinations(range(7), s):
        cnt = [q] * 7
        for i in extra:
            cnt[i] = q + 1
        out.append(cnt)
    return out


def possible(w, cnt, timeout):
    digits = "".join(str(x) for x in cnt)
    try:
        r = subprocess.run([mset, str(w), digits], capture_output=True,
                           text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "timeout"
    if "PC POSSIBLE" in r.stdout:
        return "yes"
    if "no PC" in r.stdout:
        return "no"
    return "error: " + r.stdout.strip()


def minimum(w, nmax, timeout):
    step = w // gcd(w, 4)
    n = step
    while n <= nmax:
        found = []
        undecided = 0
        for cnt in bag_multisets(n):
            r = possible(w, cnt, timeout)
            if r == "yes":
                found.append("".join(str(x) for x in cnt))
            elif r != "no":
                undecided += 1
        total = len(bag_multisets(n))
        print("    n=%-3d %3d/%-3d multisets possible, %d undecided"
              % (n, len(found), total, undecided))
        if len(found) > 0:
            return n, found[0]
        if undecided > 0:
            return None, "undecided at n=%d" % n
        n += step
    return None, "exceeded nmax"


def main():
    widths = [int(x) for x in sys.argv[1:]]
    if len(widths) == 0:
        widths = list(range(4, 17))
    timeout = float(os.environ.get("TIMEOUT", "600"))
    nmax = int(os.environ.get("NMAX", "30"))
    for w in widths:
        unconstrained = w // gcd(w, 4)
        print("w=%d  unconstrained=%d" % (w, unconstrained))
        n, witness = minimum(w, nmax, timeout)
        if n is None:
            print("w=%-3d unconstrained=%-3d sevenbag=UNRESOLVED (%s)"
                  % (w, unconstrained, witness))
        else:
            print("w=%-3d unconstrained=%-3d sevenbag=%-3d witness counts=%s"
                  % (w, unconstrained, n, witness))
        sys.stdout.flush()


main()
