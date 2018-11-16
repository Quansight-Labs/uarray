
.PHONY: clean all compare

all_targets = %-original.json %-reduced.json

.PRECIOUS: $(all_targets)

setup = import numpy as np; n = $*; A = np.arange(n); B = np.arange(n); fn = lambda a, b: (np.multiply.outer(a, b)[5]); from uarray import optimize; fn_opt = optimize(1, 1)(fn)
benchmark_command = python3 -m perf timeit -o $@ --name=$* # --track-memory
ns = $(shell seq 50 50 2000)


%-original.json:
	$(benchmark_command) -s '$(setup)' 'fn(A, B)'


%-reduced.json:
	$(benchmark_command) -s '$(setup)' 'fn_opt(A, B)'


%-all: FORCE $(all_targets)
	@echo done $*

all: $(foreach n,$(ns),$(n)-compare)
	@echo done all

%-compare: FORCE %-all
	python3 -m perf compare_to $*-*.json

compare: $(foreach n,$(ns),$(n)-compare)
	@echo compared

clean: FORCE
	rm *.json

FORCE: