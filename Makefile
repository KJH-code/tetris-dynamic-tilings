CXX      ?= g++
CXXFLAGS ?= -O2 -std=c++17
BIN      := bin

SRCS := $(wildcard src/cpp/*.cpp)
EXES := $(patsubst src/cpp/%.cpp,$(BIN)/%,$(SRCS))

all: $(EXES)

$(BIN)/%: src/cpp/%.cpp | $(BIN)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(BIN):
	mkdir -p $(BIN)

# Re-verify the claims that appear in the notes and in the paper.  Every item
# here has a matching row in the verification ledger kept with the notes.
#
# Never pipe a checker into `head`: SIGPIPE kills the checker, the pipeline's
# status is head's, and make reports success over a crashed check.  `sed -n`
# reads its whole input, so it is safe.
check: all
	@echo "== Lemma 0: column counting, minimal R per piece and width =="
	@python3 src/py/colcount.py
	@echo
	@echo "== Lemma 0 at arbitrary width: period of the reachable-state sets =="
	@python3 src/py/colproof.py
	@echo
	@echo "== Theorems 1, 5: no perfect clear for S alone, or for {S,Z} =="
	@./bin/pc3 4 2 8 0 | sed -n 1p
	@./bin/pc3 6 3 8 0 | sed -n 1p
	@./bin/pc3 5 5 8 0 | sed -n 1p
	@./bin/pc3 4 2 24 0 | sed -n 1p
	@./bin/pc3 6 6 24 0 | sed -n 1p
	@echo
	@echo "== Theorems 2, 4: O needs even width; J alone clears every width =="
	@./bin/pc3 5 5 2 0 | sed -n 1p
	@./bin/pc3 6 3 2 0 | sed -n 1p
	@./bin/pc3 4 2 32 0 | sed -n 1p
	@./bin/pc3 6 6 32 0 | sed -n 1p
	@echo
	@echo "== Theorem 3b: T alone, every assembled width replayed from the units =="
	@while read -r w seq; do ./bin/tplay "$$w" "$$seq" > /dev/null || exit 1; done < data/tplay-seqs.txt
	@echo "   every width in data/tplay-seqs.txt replays OK"
	@echo "   (the unit search and the R >= 4 lower bound are in check-full)"
	@echo
	@echo "== Theorem 4: unit decomposition, widths 4..60 =="
	@python3 src/py/units.py
	@echo
	@echo "== Theorem 5: two-column reduction, reachable states and words =="
	@python3 src/py/szlang.py | sed -n '1,3p'
	@echo "== Theorem 5: invariants I0..I3, independent implementation =="
	@python3 src/py/szinv.py
	@echo
	@echo "== A: dynamic T-parity identity, exhaustive (light cases) =="
	@./bin/verify 4 2
	@./bin/verify 4 3
	@./bin/verify 4 4
	@./bin/verify 5 5
	@./bin/verify 6 3
	@./bin/verify 8 2
	@./bin/verify 8 4
	@echo "   (w=6 n=6 adds 244010 sequences to reach 260423; see check-full)"
	@echo "== A: the same identity, independent Python implementation (light cases) =="
	@python3 src/py/averify.py 4 2 4 3 4 4
	@echo
	@echo "== B: the minimal odd-T perfect clear at width 4 needs 3 pieces =="
	@./bin/pc3 4 1 127 1 | sed -n 1p
	@./bin/pc3 4 2 127 1 | sed -n 1p
	@./bin/pc3 4 3 127 1 | sed -n 1p
	@echo
	@echo "== T alone at odd width: the parity argument must be passed as 1 =="
	@echo "   (wantpar 0 wrongly reports 'no PC' -- this is the 2026-09 harness bug)"
	@./bin/pc3 5 5 4 1 | sed -n 1p
	@./bin/pc3 5 5 4 0 | sed -n 1p

# Slow items: minutes to tens of minutes each.
check-full: check
	@echo "== Theorem 3b: unit search, assembly at widths 4..80, and the lower bound =="
	@python3 src/py/tunits.py
	@echo
	@echo "== A: w=6 n=6, the 244010-sequence case =="
	@./bin/verify 6 6
	@echo
	@echo "== A: independent Python implementation, the remaining light cases =="
	@python3 src/py/averify.py 5 5 6 3 8 2 8 4
	@echo
	@echo "== D: the four order-constrained failures at bag1 = TJLISZO =="
	@./bin/fix4 TJLISZOOJZS 200000000
	@./bin/fix4 TJLISZOOLZS 200000000
	@./bin/fix4 TJLISZOLOZS 200000000
	@./bin/fix4 TJLISZOJOZS 200000000
	@echo "== D: the two survivors of the same screen =="
	@./bin/fix4 TJLISZOSLOZ 200000000
	@./bin/fix4 TJLISZOLSOZ 200000000
	@echo
	@echo "== D: 7-bag minimum piece count, widths 4..10 =="
	@python3 src/py/bagmin.py 4 5 6 7 8 9 10

clean:
	rm -rf $(BIN)

.PHONY: all check check-full clean
