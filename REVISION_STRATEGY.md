# Revision strategy: scoping review plus zero-cost empirical audit

## Decision

The previous conceptual policy article will not be resubmitted with cosmetic revisions. It will be rebuilt as a new study with three explicit components:

1. a PRISMA-ScR-aligned evidence map;
2. a global, privacy-preserving audit of public GBFS feeds; and
3. a structured audit of public operator documents.

This design retains the original lifecycle insight while adding direct, reproducible observations without purchasing hardware.

## Provisional article identity

**Working title**

> Lifecycle Data Exposure in Shared Micromobility: A Scoping Review and Global Audit of Public GBFS Feeds

**Article type**

Scoping review with cross-sectional and limited longitudinal public-data analysis.

**Core contribution**

The article will distinguish:

- fields and identifier behavior directly observed in public shared-micromobility feeds;
- practices explicitly disclosed in operator documents;
- capabilities demonstrated in target-domain technical studies;
- near-domain mechanisms that remain hypotheses for micromobility;
- normative controls that have not been tested for effectiveness.

## Changes from the rejected manuscript

### Remove or demote

- The Japanese government deployment as the central motivating case.
- Claims about generic critical-infrastructure exposure that lack a defined consequence path.
- The uncalibrated multiplicative lifecycle-risk expression.
- The three assurance tiers unless decision rules can be derived from evidence.
- Broad claims about serviced hardware beyond the studied device and service class.
- Smart-meter analogies when direct micromobility evidence answers the same question.
- Statements implying that public disclosure gaps prove absent controls or hidden collection.

### Retain and rebuild

- The six lifecycle stages as an extraction and synthesis framework.
- The distinction between telemetry generation, linkability, accessibility, persistence, and consequence.
- Procurement, service, return, and disposition controls, but only when traceable to an observed exposure path or normative source.
- Battery and non-positional telemetry as a bounded research question rather than an established universal capability.

## Planned manuscript structure

1. **Introduction**
   - define the shared-micromobility data lifecycle;
   - identify the gap between trip-data privacy, device security, public-feed standards, and lifecycle governance;
   - state the review and audit questions.
2. **Methods**
   - protocol and deviations;
   - bibliographic sources and exact searches;
   - screening and evidence-distance classification;
   - frozen GBFS registry and cross-sectional audit;
   - privacy-preserving longitudinal sampling;
   - public-document sample and codebook;
   - statistical analysis and missingness;
   - ethics and responsible reporting.
3. **Results**
   - PRISMA-ScR flow;
   - direct and near-domain evidence map;
   - public-feed reachability and field prevalence;
   - identifier-reappearance analysis, if feasible;
   - public-document disclosure coverage;
   - lifecycle framework coverage and unsupported cells.
4. **Discussion**
   - what is directly demonstrated;
   - what remains technically plausible but unverified;
   - implications for operators, cities, and sensitive deployments;
   - standards and procurement implications;
   - limitations.
5. **Conclusion**
   - concise findings bounded to the sampled evidence and public systems.

## Planned figures

1. PRISMA-ScR flow diagram.
2. Study-level evidence map by lifecycle stage and transfer distance.
3. GBFS field-prevalence plot with confidence intervals.
4. Operator-document disclosure heatmap.
5. Revised lifecycle framework showing supported, unsupported, and unassessable paths.

## Planned tables

1. Eligibility criteria and data sources.
2. Included direct target-domain studies with device, data, access path, outcome, and evidence limitations.
3. GBFS sampling and endpoint outcomes.
4. Public-document coding results.
5. Evidence-to-control traceability matrix.

Every final figure and table will be cited in first-appearance order and placed immediately after its first in-text citation. Editable English PPTX artwork and editable DOCX tables will accompany the manuscript.

## Statistical and reproducibility safeguards

- The system, not an individual vehicle, is the primary cross-sectional analysis unit.
- Operator-domain clustering will be considered in uncertainty estimates.
- Empty or unavailable feeds will not be coded as field absence.
- Field prevalence will use explicit denominators and Wilson confidence intervals.
- Exploratory comparisons will use false-discovery-rate correction.
- Longitudinal reappearance will not be labeled a completed trip or standards violation.
- Exact coordinates and raw identifiers will not be retained.
- Registry commit, checksums, search logs, code, aggregate outputs, and environment versions will be public.
- Claims will be labeled as direct evidence, documentary evidence, near-domain transfer, normative guidance, or unresolved hypothesis.

## Feasibility without a hardware budget

The zero-cost audit can provide real empirical results on:

- global public-feed availability;
- publication of vehicle-level location, timestamps, range, and battery percentages;
- the distribution of these fields across versions, regions, and operator families;
- conservative identifier-reappearance indicators;
- lifecycle-relevant disclosure coverage.

It cannot answer whether internal BMS histories persist after return or disposal. That question will remain an explicit future hardware-study requirement rather than being implied by analogy.

### Initial cross-sectional result

The prospective protocol was written before the full registry audit. The first completed audit froze 1,520 registry entries and reached 1,428 auto-discovery endpoints. Among 813 successfully retrieved, non-empty feeds that declared motorized micromobility:

- 813 (100.0%) published a vehicle identifier field;
- 808 (99.4%) published latitude and longitude;
- 629 (77.4%) published a last-reported timestamp;
- 560 (68.9%) published battery or fuel percentage;
- 802 (98.6%) published current range; and
- 643 (79.1%) published a vehicle-specific rental URI.

These are field-presence observations, not findings of privacy harm. The registry contains many systems from the same operator families, particularly Dott. Operator-domain sensitivity analysis therefore accompanies system-level estimates: 94 of 147 eligible operator domains published battery or fuel percentage in at least one feed, and 89 published it in every eligible feed observed for that domain.

## Publication strategy

A target journal will be selected only after the cross-sectional audit and preliminary screening establish the article's actual contribution. Selection criteria will include:

- acceptance of mixed scoping-review and public-data audit designs;
- fit with transportation cybersecurity, privacy engineering, digital forensics, or mobility-data governance;
- support for reproducibility supplements;
- realistic word, figure, and reference limits;
- no requirement for experimental hardware validation that the study cannot meet.

The new journal cycle should continue in a new session after the journal is selected.

## Completion gates before submission preparation

1. Protocol and deviations finalized before outcome-driven changes.
2. Search coverage and direct-study capture audited.
3. Screening decisions complete and validated.
4. GBFS collection complete with privacy review.
5. Public-document coding complete with quotations or locators.
6. Statistical analysis unit, denominators, uncertainty, and missingness verified.
7. Reviewer-style scientific critique completed before mechanical submission checks.
8. Target-journal author guidelines checked before final formatting.
