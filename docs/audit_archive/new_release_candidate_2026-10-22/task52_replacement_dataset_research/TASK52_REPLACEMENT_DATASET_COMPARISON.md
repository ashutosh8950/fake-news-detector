# TruthScan Task 52 — Replacement Dataset Comparison

Research date: 2026-10-27  
Scope: research only. No dataset, article content, model artifact, package, or processing pipeline was accessed.

## Executive recommendation

No candidate is approved for acquisition, training, public inference, model distribution, or deployment.

The best next research lead for the existing article-level Fake/Real interface is **FakeNewsNet, narrowed to a separately assessed PolitiFact subset**. Its public documentation identifies news-item collections with fake/real files and fact-checking-platform provenance. However, the maintainers explicitly state that the complete dataset cannot be distributed because of Twitter privacy policies and news-publisher copyrights. The candidate therefore remains **`BLOCKED — RIGHTS REVIEW REQUIRED`**.

The PolitiFact subset should be assessed before GossipCop because its subject matter and fact-checking provenance are closer to news-veracity research. This is a research recommendation only; it does not authorize acquisition or relabeling.

No candidate currently satisfies the requirements for a public article-submission website. The current application must remain fail-closed while dataset rights, model provenance, reproducible dependencies, evaluation validity, and public-release authorization remain unresolved.

## Candidate comparison

| Candidate | Documented unit and labels | Fit for Track A | Provenance confidence | Public-use rights confidence | Scientific risks | Status |
|---|---|---|---|---|---|---|
| **FakeNewsNet — PolitiFact subset** | News items collected around PolitiFact ground truths; repository exposes `politifact_fake.csv` and `politifact_real.csv` metadata files. | Closest reviewed semantic fit; article-level inputs are plausible, but exact article text and label construction require candidate-specific review. | Moderate for published repository identity; exact future acquisition and file identity unverified. | Low. Complete data is not distributed because of Twitter privacy and publisher copyright constraints. | Political-domain bias, old articles, fact-checker selection effects, duplicate/syndicated content, source and URL leakage. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| **CoAID** | COVID-19 healthcare misinformation involving website news, social posts, engagements, and ground-truth labels. | Could support a narrowly scoped health-misinformation classifier, not a general-purpose public Fake/Real service. | Moderate for the documented release history; exact artifact and current terms require review. | Low/unresolved for article text, linked sources, social data, public hosting, and model distribution. | Strong topic and time bias, label/source artifacts, social-platform restrictions, class imbalance and duplicate handling. | `RESEARCH LEAD — NOT APPROVED` |
| **Zenodo Disinformation Detection v1.1** | Record describes labelled fake/disinformation and true-news datasets and code; v1.1 published 2026-01-02. | Structurally closest to the requested binary interface among the reviewed candidates. | Moderate for the Zenodo record; contents and transformation lineage were not inspected. | Low/unresolved. Record states CC BY 4.0 for the dataset package, but that does not establish rights in every underlying article. | Unknown label construction, multilingual/domain composition, duplication, source leakage, and reproducibility until archive contents are approved and inspected. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| **Fakeddit v2.0** | Reddit submissions with text, metadata, comments, images, and fine-grained labels; paper results use multimodal samples. | Not a drop-in article-level replacement; would require a text-only or multimodal redesign. | Moderate for repository/paper identity; exact retained components unverified. | Low/unresolved for Reddit/user content, comments, images, and public model use. | Distant supervision, platform/user-content restrictions, subreddit/user/source leakage, multimodal distribution shift. | `NOT SUITABLE FOR TRACK A` |
| **NELA-GT releases** | Article collections with source-level reliability/credibility labels, not article-truth labels. | Not suitable without changing the target from article truth to source reliability. | Moderate for published release identity; exact local acquisition not established. | Low/unresolved; official repository warns that collected articles may be copyrighted and describes text transformation. | Source memorization, source-label confounding, within-source variation, temporal drift. | `NOT SUITABLE FOR TRACK A` |

## Candidate-specific assessment

### 1. FakeNewsNet — recommended for further assessment only

The official repository identifies four minimal metadata files: PolitiFact fake/real and GossipCop fake/real. It documents fields such as ID, URL, title, and tweet IDs. The paper describes a repository combining news content, social context, and spatiotemporal information, and explains that PolitiFact and GossipCop represent different domains.

This is the closest fit to an article-level fake/real research interface, but it is not a rights-cleared public website dataset. The repository says complete data cannot be distributed because of Twitter privacy policies and news-publisher copyrights; its collection code uses external websites and Twitter credentials. A future assessment must determine exactly which fields may be retained, whether article text may be used for training, whether model weights may be distributed, and whether a public inference service is permitted.

The PolitiFact and GossipCop portions should not be pooled without an approved domain policy. Political and entertainment-gossip items have different topics, language, source patterns, and label processes. A model can learn domain or publisher cues rather than general article-veracity signals.

### 2. CoAID

The official repository and paper describe a COVID-19 healthcare misinformation dataset containing website news, social-platform posts, engagement data, and ground-truth labels. The paper records multiple release versions and states that Twitter terms limited released data to tweet IDs for some components.

CoAID may support a narrowly framed COVID-health misinformation study. It is not a defensible general replacement for a public website accepting arbitrary visitor articles because its topic, time period, source mix, and public-health context are highly restricted. Its article and social components need separate rights and retention review.

### 3. Zenodo v1.1

The official record identifies version v1.1, creator Sadam Hussain, a 2026-01-02 publication date, code and dataset archives, and a stated CC BY 4.0 dataset package license. These are facts about the record, not proof that the uploader can sublicense every embedded article, image, metadata field, or source.

The archive contents were not downloaded or inspected. Label definitions, collection methodology, exact article coverage, duplicates, source leakage, and transformations therefore remain unverified. It cannot be recommended beyond a rights-and-contents assessment.

### 4. Fakeddit

The official repository describes a multimodal benchmark based on Reddit submissions and provides separate text/metadata, image, and comment components. It warns that the paper results use multimodal samples and instructs users to read the Usage section. This is valuable for multimodal misinformation research but not a direct replacement for TruthScan's article-text contract.

Reddit user content, comments, images, URLs, and platform restrictions require component-specific rights review. A text-only model would be a new task and should not be presented as equivalent to the published multimodal benchmark.

### 5. NELA-GT

Task 51 already assessed NELA-GT. Its official repository documents article fields but source-level labels such as Reliable, Unreliable, Mixed, and Null. Those labels cannot be treated as article-level truth without an explicitly approved scientific redesign. NELA-GT remains a possible source-reliability research dataset, not a Track A replacement.

## Rights analysis for the public website

For every candidate, the following questions remain open:

- Does the dataset package license cover the exact article text and metadata retained by the project?
- Did the publisher or maintainer have authority to grant those rights?
- May the material be used to train a model intended for public inference?
- May trained weights be distributed or hosted by a third party?
- May raw or transformed data, URLs, excerpts, images, comments, or social identifiers be redistributed?
- Are attribution, share-alike, privacy, deletion, takedown, and retention obligations defined?
- Does public inference on visitor-submitted text create a separate privacy/security obligation?

Public availability, a paper, a repository license, or a hosting-platform label is not sufficient evidence for these uses. A qualified rights review is required where the exact terms do not answer the proposed scope.

## Scientific validity and leakage plan

No evaluation was performed. Before any candidate could support a claim about article-level performance, the owner would need to approve:

1. An exact candidate release and immutable acquisition record.
2. A label policy that preserves the source's documented semantics.
3. Publisher/source-grouped splits so the same source cannot appear across partitions.
4. Exact and near-duplicate detection across titles, URLs, syndicated text, and fact-check pages.
5. A time-aware validation and final test set.
6. Training-only fitting for preprocessing, vocabulary, feature selection, and calibration.
7. Baselines using source-only, URL/domain-only, title-only, and text-only features to expose shortcut learning.
8. Per-class precision, recall, macro-F1, balanced accuracy, calibration, abstention coverage, and out-of-domain tests.
9. A report that treats benchmark performance as dataset performance, not general truth-detection accuracy.

## Public-submission risks

Even with an approved training corpus, a public website would face:

- distribution shift from historical benchmark articles to current visitor submissions;
- unsupported languages, topics, formats, and sources;
- unknown publishers and articles outside the training domain;
- stale labels and changing factual context;
- pressure to turn probabilistic classification into a factual verdict;
- privacy and retention risk for submitted article text;
- prompt/content abuse, denial-of-service, oversized requests, and malicious input;
- model extraction and adversarial examples;
- lack of evidence retrieval or human review.

The product must use non-definitive wording, expose abstention/unavailable states, define retention, and avoid claiming that a Fake/Real output proves factual truth.

## Recommended next action

Authorize one **research-only FakeNewsNet PolitiFact candidate assessment**. The assessment should be limited to official documentation and rights questions until the owner explicitly authorizes any acquisition. It must produce:

- exact release/repository revision;
- field-by-field data and rights inventory;
- label and fact-checking methodology review;
- publisher/Twitter/privacy restrictions;
- candidate-specific source, duplicate, and temporal split plan;
- public inference, model distribution, and data-retention decision matrix.

If that assessment cannot establish rights for the intended public scope, stop without acquisition and retain the current fail-closed application. Do not substitute NELA-GT labels, FEVER labels, or source-reliability labels for article-truth labels.

## Evidence limitations

The candidate facts above were checked against the official URLs listed in `TASK52_SOURCE_REGISTER.md` on 2026-10-27. No dataset file, row, archive, article, model, or package was downloaded or inspected. Rights conclusions are release-readiness classifications, not legal opinions. Exact downstream permissions remain unresolved unless explicitly stated by an authoritative source.

**Conclusion:** `BLOCKED — RIGHTS REVIEW REQUIRED` for all candidates for the intended public website. FakeNewsNet PolitiFact is the recommended research-only next assessment; it is not approved for use.
