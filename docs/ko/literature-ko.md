# 선행연구 조사 및 신규성 판정

조사일: 2026-09-12. 조사 범위: Walkup 계열 정적 타일링, 테트리스 복잡도 계열,
테트리스 커뮤니티 실전 지식.

## 판정 요약

| 우리 결과 | 신규성 | 근거 |
|---|---|---|
| A 동적 T-패리티 정리 | **겹침** | Hard Drop Wiki 등에 실질 동일 내용 |
| B w=10 최소 홀수-T PC = 10 | 살아있음 | A의 응용. 단독 주장으로는 약함 |
| **C 단일 조각 동적 PC 분류** | **살아있음** | 문헌의 빈 칸 |

## 왜 C 가 비어 있나

두 문헌 줄기가 각각 한 변수씩만 건드렸다.

                     정적 (클리어 없음)          동적 (클리어 있음)
    단일 조각        Walkup, Hochberg,          ← 여기가 빈 칸
                     Korn-Pak, Zhan, Reid
    7종 전부         자명                        Hoogeboom-Kosters

Hoogeboom-Kosters 는 7종 전부로 "거의 모든 배치가 구성 가능" 을 보였고,
조건이 총 칸 수 나눗셈뿐이라 사실상 제약이 없다.
Walkup 줄기는 단일 조각이지만 정적이다.
단일 조각 x 동적 이 빈 칸이고, 거기서 답이 자명하지 않다.

MIT Hardness Group 이 2026 년에 단일 조각 복잡도를 다뤘으므로 이 각도 자체는
현재 살아있는 관심사다.

## 문헌별 상세

### Walkup 계열 (정적, 단일 조각)

- **Walkup 1965**, Covering a rectangle with T-tetrominoes, Amer. Math. Monthly 72, 986-988.
  T 만으로 w x n 직사각형을 덮을 수 있는 필요충분조건은 w, n 이 둘 다 4 의 배수.
  우리 C 의 정면 대비 대상. **논문의 진입점.**

- **Hochberg 2015**, The Gap Number of the T-Tetromino,
  Discrete Math. 338 (2015) 130-138, arXiv:1403.6730. (서지 2026-09-15 확인)
  gap number 를 5, 6, 7, 9 중 하나로 좁혔다.
  Walkup 조건을 못 맞추는 직사각형에 모노미노를 허용했을 때 최소 개수 M(w,n).
  fringe digraph + Bellman-Ford 로 하한 증명:
      폭 5  -> 5 열마다 모노미노 최소 1 개
      폭 7  -> 7 열마다
      폭 9  -> 17 열마다
      폭 11 -> 35 열마다
      폭 13, 15 -> 실린더 존재 (임의 열을 모노미노 없이 덮을 수 있음)
  **우리 결과는 이 하한을 전부 무효화한다** (줄 클리어 허용 시 모노미노 0 개).
  또한 Hochberg 는 S-테트로미노의 gap cap 이 무한일 것이라 추측 —
  우리의 S/Z 동적 불가능 정리와 같은 방향.
  참고: 이 논문 Theorem 1 은 고등학생 Madeline Sargent 가 증명했다고 감사문에 명시.

- **Korn-Pak 2004**, Tilings of rectangles with T-tetrominoes,
  TCS 319 (2004) 3-27. (서지 2026-09-15 확인)
  4m x 4n 타일링의 local move connectivity, Tutte 다항식과의 연결. 높이함수 도입.
  미확인: 그 높이함수가 우리 phi 와 관계있는지. 정적이라 겹칠 확률은 낮음.

- **Zhan 2012** (preprint), Tiling a deficient rectangle with T-tetrominoes.
  mn = 1 (mod 4) 인 직사각형에서 모노미노 1 개만 남기는 것이 불가능함을 증명.
  원문 미확인. Hochberg 가 요약. 2 차 인용 가능.

- **Reid 2005**, Klarner systems and tiling boxes with polyominoes,
  JCTA 111(1) (2005) 89-105. (서지 2026-09-15 확인)
  T 를 (8n-4)-omino 류로 일반화. 정적 프레임워크. 미확인이나 겹칠 확률 낮음.

- 기타: Merino 2008 (4m x 4n 타일링 개수), Feller-Hochberg 2024 (등차수열),
  Torres-Vallejo 2024 (gap cap <= 6), Goddard 2007.
  전부 정적.

### 테트리스 복잡도 계열 (동적)

- **Brzustowski 1992**, Can you win at Tetris?, MSc thesis, UBC.
  **무한 생존**이 주제. 단일 조각이면 무한히 플레이 가능, 일부 2 조각 조합도 가능.
  퍼펙트 클리어와 무관. **겹치지 않음.**

- **Burgiel 1997**, How to lose at Tetris, Math. Gazette 81, 194-200.
  S/Z 교대 수열이 필패를 강제. Walkup 을 인용한다는 점이 우리 프레이밍에 유리.
  **겹치지 않음.**

- **Hoogeboom-Kosters 2003/2004**, How to construct Tetris configurations,
  IJIGS 3(2), 97-105. (LIACS TR 2003-8)
  **쪽수 미해결**: 2026-09-15 웹 검색은 94-102 로 나왔다. 이 노트와 README 는 97-105 다.
  원문 PDF 와 dblp 접근이 차단돼 판정하지 못했고 어느 쪽도 고치지 않았다. 투고 전 확정 필요.
  **가장 인접한 선행연구.** Theorem 3: p 개 칸을 가진 배치가 빈 보드에서
  구성 가능할 필요충분조건은 (1) 꽉 찬 줄 없음 (2) 최상단 아래 빈 줄 없음
  (3) w = 0 (mod 4) 이면 p = 0 (mod 4); w = 2 (mod 4) 이면 p = 0 또는 2 (mod 4).
  그들의 Lemma 1: u*w + p = 0 (mod 4), u = 지운 줄 수.
  -> 이건 **총 칸 수 나눗셈 조건**이지 체커판 패리티가 아니다. 우리 A 와 다름.
  -> 우리 보조정리 0 (열별 정확히 R) 보다 약함. 단 그들은 7 종 전부 사용.
  **겹치지 않음. 단 반드시 인용해야 함** — 동적 구성 가능성의 원조.

- **Demaine-Hohenberger-Liben-Nowell 2003/2004**, Tetris is hard, even to approximate.
  오프라인 최적화 NP-complete. 복잡도. **겹치지 않음.**

- **Baccherini-Merlini 2008**, Combinatorial analysis of Tetris-like games, Discrete Math 308.
  Schutzenberger 방법론 + 확률생성함수로 평균 점수 분석. 오토마타 등가성.
  타일링·PC 와 무관. **겹치지 않음.**

- **MIT Hardness Group 2026**, Tetris is Hard with Just One Piece Type,
  **FUN 2026 (LIPIcs vol. 366, art. 32)**, arXiv:2603.09958. (서지 2026-09-15 확인)
  O 를 제외한 모든 테트로미노 P 에 대해, SRS 하에서 P 만으로
  **초기 보드가 주어진** clearing / survival 이 NP-hard.
  I 조각에 대한 23 년 된 추측을 반증. 도미노는 다항시간.
  **따름정리로 7k-bag 랜더마이저 하의 Tetris clearing NP-hard 가 들어 있다** —
  우리 D 절과 직접 닿는 유일한 최신 문헌이므로 논문에서 반드시 언급할 것.
  -> 문제가 다르다: 그들은 **주어진 보드의 복잡도**, 우리는 **빈 보드에서의 가능성**.
  **겹치지 않음. 단일 조각 각도가 현재 활발하다는 증거로 인용.**

- Hoogeboom-Kosters 2004, Tetris and Decidability, IPL 89.
  Hoogeboom-Kosters 2005, The Theory of Tetris (비심사 서베이). 미확인.

### 커뮤니티 지식 (A 와 겹치는 부분)

- **Hard Drop Tetris Wiki — Parity / Perfect Clear Opener**
  체커판 색칠, T 만 3-1 로 불균형, 나머지 6 종은 2-2.
  줄 클리어가 홀수 개 칸을 홀수 행만큼 떨어뜨릴 때 패리티가 바뀜.
  "지워진 줄 아래에 홀수 개 빈 칸이 있는 싱글 클리어는 T 하나와 패리티 효과가 같다.
   짝수면 효과 없음. 인접한 2 줄 또는 4 줄 동시 클리어도 효과 없음."
  -> **우리 A 와 실질적으로 같은 내용.** 증명은 없고 w=10 실전용.

- galactoidtetris.wordpress.com, howtotetris.com (Galactoid 저)
  같은 내용의 실전 가이드. "functional parity" 용어 사용.

- 우리가 추가로 가진 것: 임의 폭으로의 일반화, 홀수 폭의 A 보정항,
  mod 4 per-event 형태, 증명, PC 수열 260,423 개 전수 검증.
  -> **"새 정리" 가 아니라 "알려진 실전 규칙의 형식화 및 일반화"** 로 포지션.

## 권장 논문 구성

    제목   Tetromino tilings with line clears
           또는 Walkup's theorem fails in the dynamic setting

    1 서론   Walkup 1965 -> Hochberg gap number -> 자연스러운 질문:
             줄 클리어를 허용하면? Hoogeboom-Kosters 는 7 종 전부로 답했다.
             단일 조각은?
    2 모델   동적 타일링의 형식적 정의. 하드드롭 명세.
             어떤 결과가 모델 의존이고 어떤 게 아닌지 명시.
    3 도구   보조정리 0 (열 카운팅), 보조정리 M (거울 대칭)
    4 주결과 단일 조각 완전 분류
               I 전 폭 / O 짝수 폭 / T 전 폭 n=w / S,Z 불가능
             따름정리: Walkup 조건과 Hochberg 하한이 동적으로 무너진다
    5 부록   PC 패리티 규칙의 형식화 (커뮤니티 출처 명시)
    6 미해결 J, L 의 w=7 n=14, w=9 n=18

## 남은 확인 항목

1. Korn-Pak 높이함수 vs 우리 phi — 관계 확인
2. Zhan 2012 원문 (preprint, 입수 난이도 높음. 2 차 인용으로 대체 가능)
3. Reid 2005 (겹칠 확률 낮음)
4. Hoogeboom-Kosters, The Theory of Tetris 2005 서베이 본문
5. **Hard Drop Wiki 패리티 규칙의 최초 출처 추적** (포럼 원글).
   A 를 어떻게 인용할지 결정하는 문제. 못 찾으면
   "테트리스 커뮤니티에 널리 알려진 사실" 로 각주 처리.

1-3 은 겹칠 확률이 낮다. 5 는 논문 작성 시 필요.
