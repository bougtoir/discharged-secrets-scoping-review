# Public-document retrieval notes

The automated verifier received successful 2xx responses for 19 of 22 seeded URLs.

Three documents require browser-assisted or manual retrieval:

- **Lime privacy notice:** the page is publicly discoverable and browser-readable, but the automated request returned HTTP 403.
- **Bolt privacy notice:** the page is publicly discoverable and browser-readable, but the endpoint returned HTTP 308 without a usable `Location` header to the verifier.
- **nextbike Czech Republic data privacy policy:** browser retrieval succeeded, while the automated request returned HTTP 404.

These cases remain in the audit corpus with their automated retrieval status. A browser success will not be silently converted into an automated HTTP 200 result.
