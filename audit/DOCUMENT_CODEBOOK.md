# Public-document audit codebook

## Unit of analysis

The primary unit is an operator-document pair. Multiple jurisdictional versions are separate units when their substantive text differs.

## Values

- `explicit`: the document directly names the data or practice;
- `partial`: the document describes a broader category that plausibly contains it;
- `not_found`: the document was reviewed and no applicable statement was found;
- `not_applicable`: the domain does not apply to the document or service;
- `unavailable`: the document could not be accessed.

`not_found` is not evidence that the operator does not collect data or perform the practice.

## Coding domains

1. precise or approximate location;
2. trip start, trip end, duration, or timestamp;
3. vehicle identifier or other persistent identifier;
4. battery level, range, state, or diagnostic data;
5. fault, maintenance, repair, or customer-support records;
6. account, payment, application, and user-device data;
7. analytics, profiling, fraud detection, or automated decisions;
8. retention period or retention criteria;
9. processors, subprocessors, contractors, and maintenance providers;
10. international transfer or hosting jurisdiction;
11. access, deletion, correction, objection, or portability rights;
12. security incident contact or notification;
13. vulnerability-disclosure channel;
14. recall, return, resale, recycling, or disposal handling.

## Evidence capture

Every non-`not_found` code requires:

- source URL;
- document title and version or update date;
- access date;
- short quotation or precise section locator;
- coder note explaining the category without inferring undisclosed behavior.
