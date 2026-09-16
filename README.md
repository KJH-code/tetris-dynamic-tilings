# Tetromino tilings with line clears

Which tetromino types can empty a Tetris board?

A classical question asks which rectangles can be tiled by a single tetromino type.
Walkup (1965) proved that the T-tetromino tiles a `w × n` rectangle only when
`4 | w` and `4 | n`. Hochberg (2015) measured how far other regions are from
tileable, via the *gap number* — the minimum number of monominoes that must be left
over — and proved, for instance, that width 5 needs at least one monomino every
5 columns.

This repository asks the same question in a **dynamic** setting: the board is filled
one piece at a time under gravity, and **full rows are removed**. A *perfect clear*
is a play from the empty board back to the empty board.

**Main result.** Line clears collapse the static obstruction almost completely.

| piece | static gap cap | dynamic (this work) |
|---|---|---|
| I | 4 | every width |
| O | ∞ | even widths only |
| T | ≤ 6 | every width, `n = w` pieces |
| J, L | 4 | every width |
| **S, Z** | conjectured ∞ | **never, at any width** |

S and Z are the only tetrominoes that line clears cannot rescue. The classification
extends to every subset of the seven types:

> A piece set `P` admits a perfect clear at width `w` if and only if `P` contains one
> of `I`, `T`, `J`, `L`, or `w` is even and `O ∈ P`.

So the only unusable pair is `{S, Z}`, `{O, S}` and `{O, Z}` need even width, and
`{O, S, Z}` — three types — still fails at every odd width, because those three
pieces have the same column profiles as `S` alone and the counting argument does not
care how many of them you are given.

## Results

**Lemma 0 (column counting).** Cells never change columns, and each line clear removes
exactly one cell from every column. So in a perfect clear with `R` cleared rows, every
column receives exactly `R` cells. This is purely combinatorial — independent of the
rotation system.

**Theorem 1.** S alone (and Z alone) admits no perfect clear at any width. For odd
widths, column counting alone gives a contradiction. For even widths, counting forces
every piece to be a vertical S starting at an even column; such a piece never reaches
relative row 0 in its even column, so cell `(0,0)` is never filled, row 0 never clears,
and the first piece's cell in row 0 is permanent.

**Theorem 3(b).** T alone admits a perfect clear at every width `w ≥ 4`, and the minimum
number of pieces is exactly `n = w` (with `R = 4` rows cleared).

The lower bound needs only the first three column equations. T has three column profiles —
`(1,2,1)` flat, `(1,3)` and `(3,1)` upright — and writing `h_c`, `p_c`, `q_c` for the number
of each starting at column `c`, column `j` receives

```
N_j = h_j + 2h_{j-1} + h_{j-2} + p_j + 3p_{j-1} + 3q_j + q_{j-1} = R
```

For `R = 1, 2, 3` the equations at `j = 0, 1, 2` have no solution in non-negative integers,
so `R ≥ 4` and `n = Rw/4 ≥ w`.

The upper bound is a unit decomposition, as in Theorem 4. A stacking unit of width 4 fills
rows 0–3 by pure stacking, and a final unit of width `m ∈ {4,5,6,7}` clears the four rows;
`w = 4a + m` covers every width, with `4a + m = w` pieces.

**This is where the contrast with Walkup is sharpest.** The stacking condition *is* a T-tiling
of a `x × 4` rectangle, so Walkup forces `4 | x` — widths 5, 6 and 7 cannot be built by
stacking at all. The final unit's line clears cover exactly the widths static tiling forbids.
(Walkup also says nothing about whether a `4 × 4` tiling can be reached under gravity, since
support is not a static-tiling concern; that it can was the real obstacle here.)

See [`docs/ko/t-widths-ko.md`](docs/ko/t-widths-ko.md).

**Theorem 4.** J and L admit perfect clears at every width `w ≥ 4`, with the minimum
number of pieces:

```
w ≡ 0 (mod 4)   n = w/2    R = 2
w ≡ 2 (mod 4)   n = w      R = 4
w odd           n = 2w     R = 8
```

The construction decomposes the board into column-disjoint units, each a fixed finite
object, so the proof reduces to four `w`-independent checks. Verified for widths 4–60.

**Theorem 5.** `{S, Z}` together admits no perfect clear at any width. Column counting
confines every piece to a two-column block, reducing the width-`w` problem to a
width-independent two-column system. Four invariants on the prefix-difference sequence
`d_j = |F₀ ∩ [0,j]| − |F₁ ∩ [0,j]|` close the argument. This is an extreme form of
Burgiel's theorem: with only S and Z you cannot merely lose — you cannot even empty
the board.

## Model independence

The proofs use only three assumptions:

1. A placed piece's four cells were empty beforehand.
2. A placed piece cannot move one row down (it locks only when supported).
3. Full rows are removed simultaneously and everything above falls.

Constructions were found under hard-drop-only search, so they transfer upward to
soft drop and to SRS with kicks. Impossibility proofs never use the drop path, so they
hold in every model. Minimum piece counts match a counting lower bound that is itself
model-independent. **The classification does not depend on the rotation system.**

See [`docs/ko/model-ko.md`](docs/ko/model-ko.md).

## Layout

```
src/cpp/    search engines
  pc3.cpp     perfect-clear BFS (width / piece count / piece mask / T parity)
  verify.cpp  exhaustive check of the dynamic T-parity identity
  mset.cpp    feasibility for a given piece multiset
  seq.cpp     fixed arrival sequence, no hold, prints the play step by step
  seqp.cpp    same, but also prints phi and the clear correction term
  tplay.cpp   replays a labelled placement list (independent check of Theorem 3b)
  fix4/5.cpp  fixed-order 7-bag solver with hold (two memo strategies)
src/py/     analysis
  colcount.py column-counting transfer DP, all pieces and widths
  units.py    Theorem 4 unit decomposition, both proof obligations
  tunits.py   Theorem 3b: unit search, assembly at widths 4..80, and the lower bound
  jfull.py    Theorem 4 J-only construction, replayed end to end per width
  jgen.py     Theorem 4 odd-width construction, generated explicitly
  jl.py       Lemma M: J and L have the same set of column profiles
  jl7.py      column solutions of one piece type, tested for realizability
  tsol.py     all column-count solutions for T alone, per width
  w7why.py    w=7, R=4, T only: which column solutions are realizable
  szlang.py   Theorem 5 two-column reduction: states and row-label words
  szinv.py    Theorem 5 invariants I0..I3, independent implementation
  sz2col.py   Theorem 5: can row 0 of a block ever be full? (same as I3)
  bag.py      Python cross-check of mset.cpp, plus the w=10 multiset sweeps
  bagmin.py   7-bag minimum piece count per width
scripts/    batch drivers for the 7-bag sweeps
data/       raw results of the large 7-bag sweeps
docs/ko/    full working notes (Korean), see INDEX.md
```

`fix2.cpp` and `fix.cpp`, named in earlier drafts of the scripts, are not in this
repository and no copy survives. They were preliminary solvers; every conclusion
they produced is reproduced by `fix4`, so nothing is lost. The scripts now call
`fix4` by default.

## Reproducing

```sh
make            # build everything into bin/
make check      # column counting, Theorems 1-5, the T-parity identity on the
                # light cases, and the minimal odd-T perfect clear at width 4
make check-full # adds the 244010-sequence case, the four order-constrained
                # 7-bag failures, and the 7-bag minimum table (slow)
```

Individual runs:

```sh
./bin/pc3 10 10 127 1        # width 10, 10 pieces, all types, odd T parity
./bin/mset 10 1111222        # can this multiset (I O T S Z J L counts) clear?
python3 src/py/colcount.py   # minimal R admitting a column-count solution
```

## Status

The single-piece and two-piece classification is complete and proved.

The dynamic T-parity identity in [`docs/ko/t-parity-ko.md`](docs/ko/t-parity-ko.md)
generalizes a rule already known to the competitive Tetris community (see the Hard Drop
wiki on Parity, and the forum thread *"Hold that T piece! A parity experiment"*). Our
contribution there is the arbitrary-width form, the odd-width correction term, and a
proof; it is not a new result.

The 7-bag material in [`docs/ko/seven-bag-order-ko.md`](docs/ko/seven-bag-order-ko.md)
reproduces observations the community's own Perfect Clear Finder can already make, with
a narrower model. It is included for completeness, not as a claim of novelty.

## References

- D. W. Walkup, *Covering a rectangle with T-tetrominoes*, Amer. Math. Monthly 72 (1965) 986–988.
- R. Hochberg, *The gap number of the T-tetromino*, Discrete Math. 338 (2015) 130–138.
- M. Korn, I. Pak, *Tilings of rectangles with T-tetrominoes*, Theoret. Comput. Sci. 319 (2004) 3–27.
- H. Burgiel, *How to lose at Tetris*, Math. Gazette 81 (1997) 194–200.
- J. Brzustowski, *Can you win at Tetris?*, MSc thesis, UBC, 1992.
- H. J. Hoogeboom, W. A. Kosters, *How to construct Tetris configurations*, Int. J. Intell. Games Simul. 3 (2004) 97–105.
- M. Reid, *Klarner systems and tiling boxes with polyominoes*, J. Combin. Theory Ser. A 111 (2005) 89–105.
- Torres, Vallejo, *Fragments that reduce the gap cap of the T-tetromino to six*, Science and Engineering Journal 17 (2024) 128–133. (given names not yet checked)
- E. D. Demaine, S. Hohenberger, D. Liben-Nowell, *Tetris is hard, even to approximate*, COCOON 2003.
- MIT Hardness Group, *Tetris is hard with just one piece type*, FUN 2026 (LIPIcs 366, art. 32), arXiv:2603.09958.

## License

MIT — see [LICENSE](LICENSE).
