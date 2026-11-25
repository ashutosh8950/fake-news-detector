# Task 38 — LIAR/Fakeddit Technical Suitability Comparison

This comparison uses published documentation only. No dataset was downloaded,
parsed, or evaluated.

| Dimension | LIAR | Fakeddit |
|---|---|---|
| Primary unit | Short political statements/claims | Reddit-derived submissions with text, metadata, comments, and images |
| Labels | Six truthfulness categories in the original description | Fine-grained fake-news categories; paper describes multiple class settings |
| Direct mapping to TruthScan 0=Fake/1=Real | No; requires an owner-approved label collapse with information loss | No; requires a new label/task definition and likely exclusion or separate handling of non-text components |
| Text shape | Short claims, not full articles | Text/title-like content plus multimodal and social context |
| Source/domain cues | PolitiFact, speakers, political context | Subreddit, author/context, image and comment metadata |
| Shortcut/leakage risk | Speaker, subject, party, venue, and source metadata may encode labels | Subreddit, post metadata, image presence, comment/social fields, and source artifacts may encode labels |
| Partition implications | Group by statement/source/speaker where justified; preserve official splits unless a new policy is approved | Group by Reddit submission/thread/media identity; account for deleted content and duplicate URLs/media |
| Preprocessing implications | Claim-level text and metadata require a new contract; current article preprocessing is not equivalent | Text-only versus multimodal preprocessing must be selected explicitly; current pipeline is not equivalent |
| Evaluation implications | Six-class or explicitly approved binary mapping; metrics are not comparable to current binary article task | Multimodal-only paper protocol differs from text-only inference; no metrics can be assumed comparable |
| Rights risk | PolitiFact and linked source material; original-source copyright and research-only language require review | Reddit platform policy, user content, comments, images, deletions, and publisher/media rights |

## Interpretation

LIAR is the closer linguistic fit for a new claim-classification experiment,
but it is not a replacement for the current article-level binary corpus.
Fakeddit offers scale and richer modalities, but it would require a materially
different task contract and stronger component-level rights controls.

Neither candidate can be substituted into the current pipeline without a new
dataset identity, label mapping, preprocessing review, grouping policy,
partition manifest, evaluation protocol, and owner authorization.

No performance or compatibility claim is made. The existing dataset’s NO-GO
decision is unchanged.
