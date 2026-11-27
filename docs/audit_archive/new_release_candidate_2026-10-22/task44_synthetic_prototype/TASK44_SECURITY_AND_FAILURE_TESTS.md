# Task 44 — Security and Failure Tests

The automated tests exercise the actual isolated contract implementation with Python’s standard `unittest` library.

Covered cases:

- valid request and strict unexpected-field rejection;
- empty and oversized claims;
- all three semantic outcomes;
- missing evidence as `INSUFFICIENT_EVIDENCE`;
- unknown outcomes and extra response fields;
- evidence incorrectly attached to insufficient evidence;
- conversion of claim outcomes to Track A `Fake`/`Real` rejected;
- default-disabled and production-environment execution rejected;
- synthetic-only UI disclaimer and placeholder evidence rendering.

The prototype has no production configuration reader, so an unapproved production setting cannot enable it: there is no live registration or production entry point to enable. A future implementation must preserve this refusal-default boundary.
