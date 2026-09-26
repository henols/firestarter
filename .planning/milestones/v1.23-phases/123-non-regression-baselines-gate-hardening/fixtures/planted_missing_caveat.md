<!-- test fixture for check_permitted_claims.py -- NOT a closing artifact; never add to _DEFAULT_TARGETS -->
<!-- Planted to trip the missing-required-caveat bucket ONLY. Zero
     forbidden phrases appear below, so a scanner run against this file
     must attribute its failure to the absent caveat alone. -->

# Planted missing-caveat fixture

The native and host suites pass at their recorded case and suite counts,
and the DFU sequence is exercised against device descriptors and mocks
only. This note omits the required silicon caveat on purpose, to prove the
missing-caveat guard fires.
