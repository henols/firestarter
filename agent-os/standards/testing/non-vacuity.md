# Prove a Check Can Fail

Every new check (gate, guard, refusal) ships with committed tests that feed it violating input and assert that it refuses.

```python
def test_is_affected_true_at_bit_19(): ...                   # refuses
def test_is_affected_false_at_bit_18(): ...                  # boundary: passes
def test_require_acknowledged_no_bus_key_raises_fail_closed(): ...  # absent evidence
```

- Test both sides of each threshold.
- For a fail-closed check, test `None` / empty / missing input.
- The violation is in the input data (synthetic pin map, bad page size). Never mutate source to plant it.
- A test written before the fix must fail on its own assertion. If it fails on setup or lookup, the test is broken, not the code. Read the failure message.
- Assertions on shipped data use exact counts (`== 746`), never floors (`>=`). A change updates the number on purpose.
