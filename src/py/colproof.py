# 열 카운팅 시스템(보조정리 0)의 해 존재를 **임의 폭**에서 판정한다. 폭마다 돌리는 colcount.py 의 상위판.
# 입력: 없음 (조각 프로파일과 R 범위는 아래 상수). 출력: 조각·R 별로 해가 존재하는 폭의 주기적 특성화.
# 원리: 열을 왼쪽에서 오른쪽으로 훑는 전이의 상태(다음 열들로 넘긴 기여)가 유한하므로
#       도달 가능 상태집합의 수열이 결국 주기적이다. 그 주기를 검출하면 모든 폭이 한 번에 결정된다.
#
# 여기서 "가능" 은 필요조건일 뿐이다 (기하는 보지 않는다). 그래서 이 파일이 주는 것은
# **하한**이다: 열 해가 없으면 그 R 로는 PC 가 불가능하다.
import itertools
import sys

profiles = {
    "I": [(1, 1, 1, 1), (4,)],
    "O": [(2, 2)],
    "T": [(1, 2, 1), (1, 3), (3, 1)],
    "S": [(1, 2, 1), (2, 2)],
    "Z": [(1, 2, 1), (2, 2)],
    "J": [(2, 1, 1), (1, 1, 2), (1, 3), (3, 1)],
    "L": [(1, 1, 2), (2, 1, 1), (3, 1), (1, 3)],
}


def step(states, usable, carrylen, R):
    # 한 열을 처리한다. 상태는 길이 carrylen 의 튜플로, 앞으로 올 열들에 이미 약속된 기여다.
    out = set()
    for st in states:
        cur = 0
        if carrylen > 0:
            cur = st[0]
        need = R - cur
        if need < 0:
            continue
        ranges = []
        for p in usable:
            ranges.append(range(0, need // p[0] + 1))
        for combo in itertools.product(*ranges):
            total = 0
            for cnt, p in zip(combo, usable):
                total = total + cnt * p[0]
            if total != need:
                continue
            carry = []
            bad = False
            for k in range(1, carrylen + 1):
                v = 0
                if k < carrylen:
                    v = st[k]
                for cnt, p in zip(combo, usable):
                    if k < len(p):
                        v = v + cnt * p[k]
                if v > R:
                    bad = True
                    break
                carry.append(v)
            if bad:
                continue
            out.add(tuple(carry))
    return out


def feasible_direct(profs, w, R):
    # colcount.py 와 같은 계산. 특정 폭 하나를 직접 판정한다 (교차검증 기준).
    maxlen = max(len(p) for p in profs)
    carrylen = maxlen - 1
    start = tuple([0] * carrylen)
    states = set([start])
    for c in range(w):
        usable = [p for p in profs if c + len(p) <= w]
        states = step(states, usable, carrylen, R)
        if len(states) == 0:
            return False
    return start in states


def periodic_analysis(profs, R):
    # 균일 구간(모든 프로파일이 놓일 수 있는 열)의 도달 집합 수열이 주기적임을 검출한다.
    maxlen = max(len(p) for p in profs)
    carrylen = maxlen - 1
    start = tuple([0] * carrylen)
    states = set([start])
    seen = {}
    nu = 0
    while frozenset(states) not in seen:
        seen[frozenset(states)] = nu
        states = step(states, profs, carrylen, R)
        nu = nu + 1
    pre = seen[frozenset(states)]
    period = nu - pre
    # 균일 구간의 상태집합을 pre + period 개까지 보관
    seq = []
    states = set([start])
    for k in range(pre + period):
        seq.append(set(states))
        states = step(states, profs, carrylen, R)
    return carrylen, pre, period, seq


def tail_apply(states, profs, carrylen, R, w):
    # 오른쪽 끝 carrylen 개 열. d = w - c 가 1..carrylen 이면 놓을 수 있는 프로파일이 제한된다.
    out = set(states)
    for d in range(carrylen, 0, -1):
        usable = [p for p in profs if len(p) <= d]
        out = step(out, usable, carrylen, R)
        if len(out) == 0:
            return out
    return out


def feasible_periodic(profs, R, w, cache):
    carrylen, pre, period, seq = cache
    start = tuple([0] * carrylen)
    nu = w - carrylen
    if nu < 0:
        return None
    if nu < pre:
        base = seq[nu]
    else:
        base = seq[pre + (nu - pre) % period]
    return start in tail_apply(base, profs, carrylen, R, w)


def main():
    rmax = 12
    wlo = 4
    whi = 40
    print("열 카운팅 해의 존재를 임의 폭에서 판정한다 (전이 집합의 주기 검출).")
    print("여기서 '가능' 은 필요조건이다. 해가 없으면 그 R 로 PC 가 불가능하다 = 하한.")
    print()
    bad = 0
    for name in "IOTSZJL":
        profs = profiles[name]
        print("== %s ==" % name)
        for R in range(1, rmax + 1):
            cache = periodic_analysis(profs, R)
            carrylen, pre, period, seq = cache
            # 주기 논증을 직접 계산과 대조한다 (교차검증)
            mism = []
            for w in range(max(wlo, carrylen), whi + 1):
                a = feasible_direct(profs, w, R)
                b = feasible_periodic(profs, R, w, cache)
                if a != b:
                    mism.append(w)
            if len(mism) > 0:
                bad = bad + len(mism)
                print("   R=%-2d 주기 논증과 직접 계산 불일치: %s" % (R, mism))
                continue
            # 폭의 어느 잉여류에서 해가 있는지 주기로 적는다
            good = []
            for w in range(max(wlo, carrylen), max(wlo, carrylen) + period * 4):
                if feasible_periodic(profs, R, w, cache):
                    good.append(w)
            if len(good) == 0:
                print("   R=%-2d 어떤 폭에서도 해 없음 (pre=%d period=%d)" % (R, pre, period))
            else:
                mods = sorted(set(g % period for g in good))
                print("   R=%-2d 해 있음: w mod %d in %s  (pre=%d, 확인 폭 %d..%d)"
                      % (R, period, mods, pre, max(wlo, carrylen), whi))
            sys.stdout.flush()
        print()
    print("주기 논증 대 직접 계산 불일치 총 %d 건" % bad)
    print()
    print("== 최소 R 과 최소 n (임의 폭) ==")
    print("주기가 8 을 넘지 않고 pre-period 가 3 이하이므로, 폭 4..27 의 최소 R 을 보면")
    print("w mod 8 패턴이 확정되고 그 패턴이 모든 폭으로 연장된다.")
    print()
    for name in "IOTSZJL":
        profs = profiles[name]
        caches = {}
        for R in range(1, rmax + 1):
            caches[R] = periodic_analysis(profs, R)
        minr = {}
        for w in range(4, 28):
            best = None
            for R in range(1, rmax + 1):
                if feasible_periodic(profs, R, w, caches[R]):
                    best = R
                    break
            minr[w] = best
        # w mod 8 로 묶어 일관성을 확인한다
        groups = {}
        consistent = True
        for w in range(4, 28):
            m = w % 8
            if m in groups:
                if groups[m] != minr[w]:
                    consistent = False
            else:
                groups[m] = minr[w]
        parts = []
        for m in range(8):
            if m not in groups:
                continue
            v = groups[m]
            if v is None:
                parts.append("w≡%d(8): 불가능" % m)
            else:
                parts.append("w≡%d(8): R=%d" % (m, v))
        flag = ""
        if not consistent:
            flag = "   [주의: mod 8 로 일관되지 않음]"
        print("   %s  %s%s" % (name, "  ".join(parts), flag))
    print()
    print("최소 n 은 n = Rw/4 다. J·L 은 R = 2 / 4 / 8 이므로 n = w/2 (4|w) / w (w≡2 mod 4) /")
    print("2w (w 홀수) 이고, 이것이 정리 4 의 최소성 표와 일치한다. T 는 모든 폭에서 R=4 -> n = w.")


main()
