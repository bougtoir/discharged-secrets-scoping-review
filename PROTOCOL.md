# Protocol: Lifecycle Data Exposure in Shared Micromobility

**Version:** 0.1

**Status:** Prospective protocol drafted before full corpus screening and GBFS data collection

**Design:** Scoping review, global public-feed audit, and structured public-document audit

**Budget:** Uses only open bibliographic metadata, public standards, public GBFS feeds, and public operator documents

## 1. Rationale

The previous manuscript proposed a lifecycle model for externally serviced, telemetry-emitting hardware but relied heavily on evidence transferred from adjacent domains. This study narrows the empirical domain to shared micromobility and separates three kinds of evidence:

1. peer-reviewed or technically documented evidence about micromobility security, privacy, telemetry, forensics, and battery-management systems;
2. direct observation of fields published through General Bikeshare Feed Specification (GBFS) endpoints; and
3. operator disclosures about collection, retention, access, maintenance, third parties, deletion, and international transfer.

The study will not allege compromise, infer sensitive facility activity, reconstruct individual trips, or treat public disclosure as proof of either security or insecurity.

## 2. Objectives

### Primary objectives

1. Map the direct and near-domain evidence for data generation, inference, retention, access, and custody transitions in shared micromobility.
2. Quantify which vehicle-level operational fields are exposed by registered public GBFS systems.
3. Assess whether identifiers can reappear after an interval of non-observation, without retaining raw identifiers or coordinates.
4. Measure how consistently major operators publicly disclose lifecycle-relevant data practices.
5. Evaluate whether the proposed lifecycle framework provides useful coverage and discrimination when applied to observed systems and disclosures.

### Research questions

- **RQ1:** What direct evidence exists that shared micromobility devices, applications, backends, diagnostic interfaces, or batteries generate or expose security- or privacy-relevant data?
- **RQ2:** How often do registered GBFS systems publish vehicle identifiers, coordinates, timestamps, battery or range indicators, reservation state, disability state, and vehicle-specific deep links?
- **RQ3:** Among a prespecified longitudinal sample, how often does the same pseudonymized public identifier reappear after an interval in which the vehicle is absent from the public feed?
- **RQ4:** Which lifecycle practices are disclosed in public operator documents, and where are disclosure gaps concentrated?
- **RQ5:** Which parts of the lifecycle framework are directly supported, indirectly supported, contradicted, or not assessable from the collected evidence?

## 3. Study components

### Work package 1: Scoping review

The review will follow the Preferred Reporting Items for Systematic Reviews and Meta-Analyses extension for Scoping Reviews (PRISMA-ScR) where applicable. It is an evidence-mapping review, not an effect-size meta-analysis.

#### Concept

Security, privacy, telemetry, battery-management data, diagnostics, digital forensics, data retention, data remanence, maintenance access, return, disposal, and related lifecycle controls.

#### Population

Shared electric scooters, shared electric bicycles, other public shared micromobility devices, their applications, backends, embedded controllers, battery-management systems, maintenance tools, and service ecosystems.

#### Context

Civilian, commercial, government, or other operational settings. Studies do not need to concern critical infrastructure directly; transfer to critical-infrastructure settings will be assessed separately.

#### Date and language limits

- Publication date: 1 January 2010 through the final search date.
- Languages: English and Japanese.
- Earlier seminal studies may be added through backward citation searching when necessary to explain a mechanism.

#### Sources

- OpenAlex
- Crossref
- IEEE Xplore metadata and search results
- ACM Digital Library metadata and search results
- arXiv
- official standards, regulatory, and government repositories
- backward and forward citation searching from included records

The limitations of not using subscription-only Scopus or Web of Science exports will be reported explicitly.

#### Core search concepts

Searches will combine terms from the following groups:

1. `"shared micromobility" OR "e-scooter" OR "electric scooter" OR "shared bicycle" OR bikeshare OR "bike share"`
2. `security OR privacy OR telemetry OR tracking OR inference OR forensic* OR diagnostic* OR vulnerability OR attack`
3. `"battery management system" OR BMS OR battery OR "state of charge" OR "state of health"`
4. `maintenance OR repair OR recall OR return OR disposal OR recycling OR "second life" OR remanence`
5. `GBFS OR "General Bikeshare Feed Specification" OR "free_bike_status" OR "vehicle_status"`

Exact database-specific strings, dates, result counts, and export files will be preserved in a search log.

#### Inclusion criteria

- Primary empirical study, reproducible technical report, systematic/scoping review, standard, regulation, or official guidance.
- Addresses at least one component of the shared-micromobility device-service ecosystem or a clearly specified near-domain mechanism.
- Reports a data field, interface, access path, inference, retention behavior, forensic capability, attack surface, control, or lifecycle transition relevant to an RQ.
- Provides enough bibliographic or source information for verification.

#### Exclusion criteria

- General commentary with no identifiable evidence or control basis.
- Studies limited to traffic safety, adoption, pricing, or environmental effects without a data-security component.
- Marketing pages without technical or governance information.
- Duplicates, inaccessible citations with no usable abstract or source record, and sources whose claims cannot be distinguished from secondary reporting.
- Offensive details whose inclusion would materially facilitate unauthorized access; high-level defensive findings may still be coded.

#### Screening

One reviewer will perform title/abstract screening and full-text screening because the project has no review budget. To reduce error:

1. eligibility criteria will be piloted on the first 30 records;
2. ambiguous decisions will be logged with reasons;
3. excluded full texts will receive a coded exclusion reason;
4. a randomly selected 20% of records will be re-screened in a delayed second pass;
5. disagreements between passes will be resolved before extraction;
6. single-reviewer screening will remain an explicit limitation.

### Work package 2: Public GBFS audit

#### Sampling frame

The sampling frame is the MobilityData GBFS `systems.csv` registry frozen at a named Git commit and SHA-256 checksum. The initial exploratory registry contained 1,520 systems across 48 country codes; final counts will be recalculated from the frozen study version.

#### Cross-sectional census

All registry entries with an auto-discovery URL will be requested with:

- a descriptive research user agent;
- bounded concurrency;
- a 15-second timeout;
- no more than three attempts with bounded backoff;
- local caching of registry, discovery, and vehicle-type metadata during the study run.

Vehicle-status responses containing coordinates or identifiers will be reduced to aggregate counts and field-presence indicators in memory and will not be cached.

For each system, the audit will record:

- registry metadata and advertised GBFS versions;
- endpoint reachability and response status;
- feed names and declared schema version;
- presence of `vehicle_status` or `free_bike_status`;
- number of currently published vehicle records;
- presence, not value, of vehicle-level fields;
- availability of vehicle-type metadata;
- whether motorized vehicle types are declared.

The field inventory will include:

- `vehicle_id` or `bike_id`
- `lat` and `lon`
- `last_reported`
- `current_range_meters`
- `current_fuel_percent`
- `is_reserved`
- `is_disabled`
- `vehicle_type_id`
- vehicle-specific rental URIs
- station or home-station identifiers

Exact coordinates, raw vehicle identifiers, and vehicle-specific deep links will not be retained in the research dataset.

#### Longitudinal sample

Eligible systems will:

1. publish `vehicle_status` or `free_bike_status`;
2. declare or plausibly operate at least one motorized micromobility type;
3. use GBFS version 2.0 or later, where identifier rotation is a stated privacy requirement;
4. return a valid non-empty feed during the enrollment check.

Systems will be grouped by operator domain and geographic region. A deterministic random seed will select up to 60 systems while limiting dominance by any one operator family. The final sampling script and selection table will be published.

The target observation schedule is one request every 10 minutes for 48 hours. The collector will honor explicit rate limits, `ttl` values when more restrictive, and service terms. Systems that prohibit or cannot support the schedule will be excluded from longitudinal collection but retained in the cross-sectional census.

#### Privacy-preserving identifier analysis

Raw identifiers will be transformed in memory with a keyed hash. The key will not be published, and raw identifiers will not be written to disk. Stored records will contain only:

- system-level pseudonymous identifier;
- pseudonymized vehicle token;
- observation time;
- field-presence indicators;
- whether the token is present or absent.

Coordinates will be discarded before storage. The analysis will identify a **candidate identifier reappearance** when the same pseudonymized token is observed, absent for at least two scheduled observations, and later observed again.

Candidate reappearance is not equivalent to a confirmed completed rental or a standards violation. Absence may reflect maintenance, connectivity, feed filtering, or other causes. Results will therefore be described conservatively and aggregated at system or operator-family level.

### Work package 3: Public-document audit

#### Operator sample

Included motorized systems will be grouped by normalized operator website domain. The 15 operator domains represented by the largest number of eligible registry systems will form the primary document sample. Ties will be resolved alphabetically. A sensitivity sample will include up to five additional operators selected by deterministic regional stratification.

#### Documents

For each operator, the study will seek:

- privacy or data-protection notice;
- terms of service;
- GBFS or developer documentation;
- security or vulnerability-disclosure policy;
- sustainability, maintenance, battery, recycling, or end-of-life documentation;
- publicly available government contract, permit, or data-sharing requirements when directly linked from an official source.

The search date, URL, document title, jurisdiction, version or update date, access result, and archived checksum will be logged. Copyrighted full text will not be redistributed unless its license permits redistribution.

#### Coding domains

Documents will be coded for explicit disclosure of:

- precise or approximate location;
- trip and timestamp data;
- vehicle and persistent identifiers;
- battery level, range, state, or diagnostic information;
- fault, maintenance, repair, and support records;
- app, account, payment, and device data;
- derived analytics, profiling, fraud detection, or model training;
- retention duration or retention criteria;
- processors, subprocessors, contractors, and maintenance providers;
- international transfer or hosting jurisdiction;
- user access, deletion, correction, or objection rights;
- incident notification and vulnerability reporting;
- data handling during recall, return, resale, recycling, or disposal.

Coding will distinguish `explicitly disclosed`, `partially disclosed`, `not found`, and `not applicable`. `Not found` will not be interpreted as evidence that a practice does not occur.

## 4. Evidence classification

Each included source will receive a transfer-distance category:

- **D4 — Direct target-domain empirical evidence:** measurement, reverse engineering, forensics, or observation of shared micromobility devices or services.
- **D3 — Direct target-domain documentary evidence:** standards, operator documentation, contracts, regulations, or public-feed observations specific to shared micromobility.
- **D2 — Near-domain empirical evidence:** electric vehicles, battery-powered embedded systems, connected fleets, or similar serviced devices with a shared mechanism.
- **D1 — Mechanism analogy:** evidence from a materially different device class, such as smart meters, used only to establish a limited mechanism.
- **N — Normative evidence:** guidance or standards supporting controls without demonstrating exposure or control effectiveness.

Empirical and technical studies will also be described across six dimensions:

1. data provenance;
2. device and sample coverage;
3. reproducibility;
4. realism of the assumed access path;
5. validity of the measured outcome;
6. external validity.

Each dimension will be coded as `strong`, `moderate`, `weak`, or `not reported`. No opaque composite quality score will be used.

## 5. Framework assessment

The lifecycle framework will not be described as validated for effectiveness. It will be assessed for:

1. **coverage:** whether observed evidence can be mapped without creating new stages;
2. **discrimination:** whether different systems and operators receive meaningfully different evidence profiles;
3. **traceability:** whether each proposed control links to a documented exposure path or normative source;
4. **assessability:** whether public or procurable evidence could determine implementation;
5. **gaps:** which proposed controls cannot be assessed or supported.

The prior three-tier profile will be retained only if explicit decision rules can be derived. Otherwise, it will be removed or presented as a research hypothesis.

## 6. Analysis

### Descriptive analysis

- counts and proportions with 95% Wilson confidence intervals;
- median and interquartile range for record counts and disclosure-domain counts;
- field-presence heatmaps by GBFS version, region, and operator family;
- evidence maps by lifecycle stage and transfer-distance category;
- document-disclosure coverage by domain.

### Exploratory comparisons

Exploratory comparisons may use Fisher's exact test or chi-square tests for categorical outcomes. Multiple comparisons will use a false-discovery-rate correction. These analyses will be labeled exploratory and will not be interpreted causally.

Identifier-reappearance uncertainty will be estimated with confidence intervals clustered at system level. Sensitivity analyses will vary the required absence interval and exclude systems with unstable endpoint availability.

### Missingness

Endpoint failure, document unavailability, field absence, and explicit negative disclosure will remain separate states. Missing public information will not be treated as absence of collection or absence of risk.

## 7. Ethics, safety, and responsible reporting

- Only public feeds and public documents will be used.
- No authentication bypass, firmware exploitation, or unauthorized access will be performed.
- No raw coordinates, raw vehicle identifiers, or reconstructable trip histories will be retained or published.
- Results will be aggregated so that the paper does not identify sensitive routes or facilities.
- Potential nonconformity will be described as an observation requiring confirmation, not as misconduct.
- Material security findings will be handled through responsible disclosure before publication.
- The institutional determination regarding human-participant or ethics-review applicability will be recorded before submission.

## 8. Reproducibility outputs

The public repository will contain:

- this protocol and a dated deviation log;
- database-specific search strings and search log;
- deduplicated candidate-record metadata;
- screening decisions and exclusion reasons;
- study-level extraction table;
- frozen GBFS registry metadata and checksum;
- data-collection and analysis code;
- aggregate, privacy-preserving GBFS results;
- document-audit metadata and coding table;
- PRISMA-ScR flow counts;
- analysis environment and locked dependency versions;
- manuscript source, figures, tables, and submission outputs.

Raw copyrighted documents, raw identifiers, exact coordinates, secrets, and authentication material will not be committed.

## 9. Protocol deviations

Any change made after formal screening or data collection begins will be recorded in `PROTOCOL_DEVIATIONS.md` with:

- date;
- original rule;
- revised rule;
- reason;
- likely effect on results;
- whether the change was made before examining the affected outcome.

## 10. Interpretation limits

The study can quantify public field exposure, identifier behavior visible in public feeds, disclosure coverage, and the distribution of published evidence. It cannot establish:

- undisclosed backend collection;
- the full contents of a battery-management system;
- malicious intent;
- compromise of a specific operator or facility;
- effectiveness of untested controls;
- prevalence outside the observed registry and document sample;
- critical-infrastructure consequence without a separately defined deployment scenario.
