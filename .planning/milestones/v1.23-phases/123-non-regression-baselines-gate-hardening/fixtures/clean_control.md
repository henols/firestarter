<!-- test fixture for check_permitted_claims.py -- NOT a closing artifact; never add to _DEFAULT_TARGETS -->

# Clean control fixture

The ARM target builds clean under CMake. The native and host suites pass at
their recorded case and suite counts (141 cases across 17 suites; 1134
host tests, 0 skipped). The DFU sequence is exercised against device
descriptors and mocks only.

no PY32F071 hardware exists, so every claim above is scoped to what a
build, a suite run, and a mock can prove -- nothing here is a claim about
physical silicon.
