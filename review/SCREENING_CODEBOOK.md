# Screening codebook

## Screening table fields

Each record receives:

- `record_id`: stable identifier assigned from the deduplicated candidate table;
- `title_abstract_decision`: `include`, `exclude`, or `uncertain`;
- `title_abstract_reason`: coded reason when excluded or uncertain;
- `full_text_status`: `not_sought`, `retrieved`, `not_retrieved`;
- `full_text_decision`: `include`, `exclude`, or `uncertain`;
- `full_text_exclusion_reason`: required for full-text exclusions;
- `evidence_distance`: `D4`, `D3`, `D2`, `D1`, or `N`;
- `reviewer_note`: brief factual note, not an argument written after seeing results;
- `first_pass_date` and `second_pass_date`;
- `second_pass_decision`;
- `resolution`.

## Title/abstract exclusion reasons

- `E1_WRONG_DOMAIN`: no shared micromobility or transferable device mechanism;
- `E2_WRONG_TOPIC`: no security, privacy, telemetry, forensic, lifecycle, or control content;
- `E3_NO_EVIDENCE`: commentary or marketing without an identifiable evidence basis;
- `E4_DUPLICATE`: duplicate publication or version;
- `E5_DATE_LANGUAGE`: outside the protocol date or language scope;
- `E6_UNVERIFIABLE`: insufficient bibliographic information for verification.

## Full-text exclusion reasons

- `F1_NO_RELEVANT_DATA_PATH`: does not describe a relevant field, interface, inference, retention behavior, access path, or control;
- `F2_MECHANISM_NOT_TRANSFERABLE`: adjacent-domain mechanism lacks a shared technical basis;
- `F3_SECONDARY_WITHOUT_ADDED_SYNTHESIS`: secondary source adds no extractable evidence;
- `F4_NOT_RETRIEVED`: usable full text could not be obtained;
- `F5_SUPERSEDED`: superseded by a more complete version from the same study;
- `F6_UNSAFE_DETAIL_ONLY`: source cannot be summarized safely without facilitating unauthorized access.

## Decision rules

1. Target-domain evidence is not automatically included; it must answer at least one research question.
2. Adjacent-domain evidence requires an explicit shared mechanism and is coded D2 or D1.
3. Normative guidance cannot demonstrate prevalence or technical capability.
4. Public disclosure is documentary evidence, not proof of actual implementation.
5. Abstract-only evidence may be mapped but is marked as incompletely assessed.
6. Uncertainty is resolved conservatively at full text rather than excluded at title/abstract.
