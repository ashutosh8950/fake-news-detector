# Task 41 — Fallback Decision Tree

```text
Owner authorizes research-only clarification?
├─ No → Keep Zenodo blocked; abandon or defer candidate; do not acquire.
└─ Yes
   └─ Rights-holder/creator supplies verifiable evidence?
      ├─ No → Reject or defer Zenodo; research alternatives with documented provenance.
      └─ Yes
         └─ Evidence covers exact material and intended use?
            ├─ No → Keep the affected decision blocked; request narrower clarification.
            └─ Yes
               └─ Does it cover only academic/internal use?
                  ├─ Yes → Academic track may proceed only after owner approval and all technical gates;
                  │        public hosting remains blocked.
                  └─ No/unclear
                     └─ Does it separately cover public hosting and intended commercial status?
                        ├─ No → Public website remains blocked.
                        └─ Yes
                           └─ Does it cover model distribution and raw-data redistribution separately?
                              ├─ No → Preserve those activities as blocked; hosted-only operation may still
                              │        require separate privacy, security, release, and deployment approval.
                              └─ Yes → Submit the complete evidence package for qualified review and owner
                                       release approval; only then consider the existing secure preflight.
```

If the creator cannot establish relevant rights, stop this candidate and research a better-documented alternative. A different dataset’s open license must still be checked for underlying source content and intended downstream use; no license label is an automatic substitute for provenance review.

No branch authorizes downloading, processing, training, artifact creation, release, hosting, or deployment by itself.
