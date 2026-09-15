# doc_min.md — the citing document for `test_remap_citations.py`

Point citation that sits on the chain: firestarter/src/chained_demo.cpp:15
Range spanning both deleted blocks (shrinks, does not translate): chained_demo.cpp:3-18
Range whose BOTH endpoints chain (span must stay stable across runs): chained_demo.cpp:10-20
A colon_list, handled as independent points and never as a range: chained_demo.cpp:15,20
A markdown anchor point citation: chained_demo.cpp#L16
A markdown anchor range citation: chained_demo.cpp#L15-L20
A citation AT a deleted line — retarget, so it must be left exactly as written: chained_demo.cpp:12
