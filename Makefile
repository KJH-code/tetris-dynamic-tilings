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

# reproduce the main claims
check: all
	@echo "== Theorem 4: unit decomposition, widths 4..60 =="
	@python3 src/py/units.py
	@echo
	@echo "== Theorem 5: 2-column reduction, invariants I0..I3 =="
	@python3 src/py/szlang.py | head -20
	@echo
	@echo "== Column counting: minimal R per piece and width =="
	@python3 src/py/colcount.py

clean:
	rm -rf $(BIN)

.PHONY: all check clean
