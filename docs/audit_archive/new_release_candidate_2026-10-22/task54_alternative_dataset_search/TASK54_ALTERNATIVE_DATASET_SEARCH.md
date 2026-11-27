# Task 54 — Alternative Dataset Search for Track A

**Research date:** 2026-10-27  
**Scope:** public-document research only; no acquisition or implementation

## Executive conclusion

**Conclusion: `NO CANDIDATE FOUND WITH A PLAUSIBLE RIGHTS PATHWAY`.**

Five candidates not substantively assessed in Tasks 51–53 were reviewed. The PolitiFact-Oslo Corpus has the clearest article-level label fit among the new candidates, and BuzzFeed-Webis has a stable scholarly/Zenodo record with complete-article material described. Neither reviewed source establishes the downstream rights needed for a public website. PolyglotFakeFacts has a stated CC BY 4.0 dataset-package label, but the underlying-source rights and the Mendeley platform’s conflicting AI-training notice remain unresolved. ReCOVery is source-reliability research for a narrow COVID-19 period and carries an Attribution-NonCommercial-ShareAlike repository license. HinFakeNews has a promising binary Hindi schema, but its authoritative record and rights scope could not be independently verified from the accessible page.

These are research leads only. Public availability, a paper, a repository, a DOI, or a package license does not establish permission to retain third-party article text, train a model, host visitor inference, distribute weights, or use the result commercially.

## Candidate ranking

| Rank | Candidate | Documented fit to current Fake/Real interface | Main scientific risk | Rights/provenance status | Overall status |
|---:|---|---|---|---|---|
| 1 | PolitiFact-Oslo Corpus | Complete English texts individually labelled for veracity; article-level target is closest to Track A. | PolitiFact selection bias, political/event concentration, possible source and claim leakage; exact release artifact and split evidence not established. | No downstream-use license or public-hosting permission found in the reviewed official record; PolitiFact content rights remain a separate issue. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| 2 | BuzzFeed-Webis Fake News Corpus 2016 | Article corpus with professional-journalist fact-checking and a fixed DOI record. | Only seven weekdays around the 2016 US election; publisher/source and time leakage; labels reflect BuzzFeed fact-checking and selected publishers. | Zenodo record’s Rights field did not show a usable license in the inspected page; archive includes third-party articles and web archives. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| 3 | PolyglotFakeFacts v2.0 | 10,206 full-text articles in 18 languages with `fake/non-fake` labels and dates/URLs/source fields. | Label construction uses EUvsDisinfo-identified outlets versus curated “credible” sources; strong source and policy confounding; translation effects and cross-language imbalance. | Record displays CC BY 4.0, but it does not establish authority over every article. Mendeley’s page also states that all content is reserved for text/data mining and AI training unless open-access terms apply. | `BLOCKED — RIGHTS REVIEW REQUIRED` |
| 4 | ReCOVery | Full article body text and binary reliability field are documented. | Label is inherited from publisher credibility, not article truth; COVID-only, Jan–May 2020, source leakage and major domain shift. | Repository states complete data cannot be distributed because of publisher copyright/Twitter policy; repository license is CC BY-NC-SA 4.0. Public/commercial/model-use scope remains unresolved. | `NOT SUITABLE FOR TRACK A` |
| 5 | HinFakeNews | Public catalogue describes Hindi full articles with a Boolean fake/real field. | Language and India-specific domain; collection and label methodology require verification; source/label confounding is likely. | The accessible catalogue page did not expose a verifiable license, maintainer permission, immutable release, or underlying-article rights record. | `INSUFFICIENT EVIDENCE` |

## Candidate assessments

### 1. PolitiFact-Oslo Corpus

The SINTEF/University of Oslo publication describes English fake and real news samples collected from PolitiFact, complete texts that correspond to the claims, expert veracity labels, and metadata such as text type. This is the strongest semantic fit among the newly reviewed candidates because it does not require silently converting source-reliability labels into article truth.

The reviewed publication page does not provide an immutable downloadable release, package license, field-level provenance manifest, or permission for a public inference service. Since the content is tied to PolitiFact and third-party source material, the owner would need written clarification covering text retention, training, public inference, commercial use, weights, and redistribution. Until then, it is a rights-blocked research lead, not a replacement.

### 2. BuzzFeed-Webis Fake News Corpus 2016

The Zenodo record identifies a DOI/versioned dataset, nine publishers, seven weekdays around the US election, and 1,627 articles checked by professional journalists. This offers a better provenance anchor than an anonymous hosting-platform upload and may support a carefully bounded academic benchmark.

It is not suitable evidence for a general public classifier without substantial caveats. The time window is extremely narrow, the outlets are selected and grouped by political orientation/mainstream status, and a random split could reward publisher or event memorization. The record lists article and web-archive files but does not provide a usable license in the inspected Rights field. The underlying articles and archived pages therefore require rights review before retention or training.

### 3. PolyglotFakeFacts v2.0

The Mendeley record describes a versioned 2026 release with 10,206 articles across 18 languages, original and translated text, dates, URLs, source names, and `fake/non-fake` labels. It documents duplicate removal and a collection process based on EUvsDisinfo-identified unreliable outlets and country-specific credible sources.

This is structurally attractive for experimentation but has a high risk of source and selection confounding. “Fake” and “real” are not necessarily article-by-article independent truth judgements; the collection rule embeds source-level assumptions. The record labels the package CC BY 4.0, while the page’s site-wide notice says content and AI-training rights may remain reserved unless open-access terms apply. The contributor’s authority over the underlying articles and translations is not established. This must remain blocked pending field-level rights review.

### 4. ReCOVery

The official repository and paper describe 2,029 COVID-19 news articles from January–May 2020, collected from 22 reliable and 38 unreliable websites, with `body_text`, publisher, date, and a reliability value. The paper explicitly says the label is inherited from the credibility of the media outlet, which makes it a source-reliability task rather than a defensible article-truth target for Track A.

The repository states that the complete dataset cannot be distributed because of Twitter privacy policies and publisher copyrights. Its license file is Attribution-NonCommercial-ShareAlike 4.0 and itself explains that a licensor must have authority over the rights granted. This blocks the intended public/commercial route and does not cure the target-label mismatch.

### 5. HinFakeNews

The AIKosh catalogue search result describes an approximately 68,000-item Hindi corpus with political, social, and communal coverage, article URL/title/content, and a Boolean fake/real field. However, the catalogue page returned no parseable content during this review, so the exact release, publication, collection method, label authority, and license are `UNVERIFIED`.

This candidate should not be acquired or ranked as approved until an accessible authoritative release record and rights statement are supplied. Even if verified, the Hindi/domain scope would require a separate product and evaluation decision rather than silently replacing an English general-news model.

## Rights assessment for public use

No candidate currently has a documented, end-to-end rights pathway for the intended website. For any future candidate, the owner must obtain evidence separately for:

- package and metadata license;
- underlying article, image, and publisher rights;
- collection and retention of full text;
- training and internal evaluation;
- public inference on visitor-submitted text;
- commercial use;
- model-weight distribution;
- transformed-data or raw-data redistribution;
- attribution, notices, deletion, and privacy obligations.

A package license covers only what the licensor had authority to license. It does not automatically cover embedded articles, publisher archives, images, translations, user content, or platform data.

## Scientific and public-website risks

All five candidates require evaluation controls beyond a random train/test split:

- group by publisher/source and detect exact and near duplicates;
- use time-aware validation and test periods;
- fit preprocessing only on training data;
- report class balance, per-source performance, calibration, abstention, and uncertainty;
- test on publishers and topics not seen during training;
- document whether the target is article veracity, publisher reliability, or fact-checker judgement.

A benchmark score would not establish correctness on arbitrary visitor submissions. The website would face unseen publishers, new events, language and format mismatch, adversarial input, and privacy/retention obligations. Any eventual UI must describe the output as a model prediction, not a verified fact, and abstain when readiness, domain support, or confidence is inadequate.

## Single smallest next action

Do not acquire a dataset yet. The owner should choose **one** candidate for a candidate-specific rights review and define the intended scope (academic-only, public non-commercial demonstration, commercial use, model release, and data redistribution). If the owner wants the strongest technical lead, choose PolitiFact-Oslo for rights/provenance clarification; if a versioned archive is more important, choose BuzzFeed-Webis. That choice authorizes research review only, not acquisition or training.

