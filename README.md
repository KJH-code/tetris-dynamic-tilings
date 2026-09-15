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
extends to piece sets: the only unusable pair is `{S, Z}`, and every set of three or
more types works.

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
  fix4/5.cpp  fixed-order 7-bag solver with hold (two memo strategies)
src/py/     analysis
  colcount.py column-counting transfer DP, all pieces and widths
  units.py    Theorem 4 unit decomposition, both proof obligations
  szlang.py   Theorem 5 two-column reduction, invariant checks
scripts/    batch drivers
data/       raw results of the large 7-bag sweeps
docs/ko/    full working notes (Korean), see INDEX.md
```

## Reproducing

```sh
make            # build everything into bin/
make check      # re-verify Theorems 4 and 5 and the counting table
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
- E. D. Demaine, S. Hohenberger, D. Liben-Nowell, *Tetris is hard, even to approximate*, COCOON 2003.
- MIT Hardness Group, *Tetris is hard with just one piece type*, arXiv:2603.09958.

## License

MIT — see [LICENSE](LICENSE).
