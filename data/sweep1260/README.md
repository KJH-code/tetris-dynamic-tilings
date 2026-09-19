# 1,260 류 × 840 접두사 전수 — 이어서 돌리는 법

이 디렉터리의 `<bag1>.out` 은 **완료된 류**뿐이다 (840 줄). `bag1sweep.sh` 가 `.partial` 로
쓰다가 840 줄이 차면 옮기므로, 여기 있는 파일은 전부 온전하다.

스윕은 스크래치패드에서 돌고 완료분만 여기로 복사된다. 컨테이너가 회수되면 스크래치패드는
사라지고 **이 디렉터리만 남는다.** 그래서 다시 시작할 때는 먼저 되돌려 놓아야 한다.

    S=<스크래치패드>/sweep1260
    mkdir -p $S && cp -n data/sweep1260/*.out $S/
    PAR=4 ./scripts/bag1sweep.sh data/bag1-classes-1260.txt data/bag2-prefixes.txt $S

이 단계를 빼먹으면 이미 끝난 류를 처음부터 다시 돈다 (결과는 같지만 시간을 버린다).

## 1 단계가 끝난 뒤

`CAP` 과 `TIMEOUT` 줄을 모아 큰 상한으로 확정해야 한다. **그 전에는 결론이 아니다.**

    grep -H " CAP\| TIMEOUT" data/sweep1260/*.out \
      | sed 's#data/sweep1260/##; s#\.out:# #; s# \(CAP\|TIMEOUT\)##' > cap-cases-1260.txt
    PAR=4 TMO=3600 ./scripts/capresolve.sh cap-cases-1260.txt cap-resolved-1260.out

2026-09-18 에 표본 100 개에서 1 단계가 `FAIL 0` 을 냈는데 CAP 641 건 안에 실패 9 건이
숨어 있었다. 이번 스윕은 그보다 12 배 크다.

## 류 목록의 순서

`data/bag1-classes-1260.txt` 의 앞 **180 개**는 S 와 Z 가 둘 다 5 번째 이후인 류다.
이 조건은 궤도 불변이고(거울은 S↔Z 를 바꾸고, 교환은 1·2 번 자리만 건드린다),
"실패의 필요조건" 후보다. 중간에 멈춰도 이 추측에 대한 답이 먼저 쌓이도록 앞에 뒀다.
