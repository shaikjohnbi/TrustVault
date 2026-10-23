# AI Prompt and Engineering Log — TrustVault



**Project:** TrustVault — Secure Document Sharing with a Real Audit Trail

**Purpose:** Record AI-assisted development, verification, errors, corrections, and available commit evidence.

> **Transparency note:** This log distinguishes verified results from historical notes. The entries below are based on the development record available for this project. Where separate historical commits or exact error records are unavailable, that limitation is stated explicitly.

## Entry 1 — 2026-10-22 — Document Authorization

**Prompt recorded:** Help implement and test document access rules so that owners have full access, users with READ grants can only read, and users with EDIT grants can read and edit.

**AI assistance:** Guidance for a centralized `can_access_document()` helper and automated permission tests.

**Specific error:** No specific error is documented in the available record for this step.

**Correction and verification:** Implemented the centralized permission helper and tests for owner access, ungranted users, READ grants, and EDIT grants. Earlier development notes report that the document permission test suite passed 7 tests. The latest verified combined test run passed 21 tests.

**Commit evidence:** The implementation is included in the repository snapshot at [TrustVault commit f1ddb96](https://github.com/shaikjohnbi/TrustVault/commit/f1ddb96). A separate historical commit for this step is not available.

## Entry 2 — 2026-10-22 — Immediate Permission Revocation

**Prompt recorded:** Help verify that a user's access is denied immediately after their document grant is revoked.

**AI assistance:** Guidance for testing access before and after deleting a `DocumentGrant`.

**Specific error:** No separate error record is available for this step.

**Correction and verification:** Added or developed a test for access before and after grant revocation. Earlier development notes report that the document permission test suite passed. The latest verified combined test run passed 21 tests.

**Commit evidence:** See the [available TrustVault repository commit](https://github.com/shaikjohnbi/TrustVault/commit/f1ddb96). A separate historical commit for this step is not available.

## Entry 3 — 2026-10-22 — Audit Trail

**Prompt recorded:** Help test the audit event service for successful actions, denied access, anonymous actors, and event ordering.

**AI assistance:** Guidance for tests covering audit event fields, denied outcomes, missing actors, ordering, and permission grant/revocation events.

**Specific error:** No separate error record is available for this step.

**Correction and verification:** Developed audit service tests. Earlier development notes report that the audit test suite passed 6 tests. The latest verified combined test run passed 21 tests.

**Commit evidence:** See the [available TrustVault repository commit](https://github.com/shaikjohnbi/TrustVault/commit/f1ddb96). A separate historical commit for this step is not available.

## Entry 4 — 2026-10-22 — Unauthorized Document Routes

**Prompt recorded:** Help test that an ungranted user cannot view or download another user's private document.

**AI assistance:** Guidance for Django client tests using an unrelated authenticated user to request document detail and download endpoints.

**Specific error encountered:** The download test initially expected HTTP 403, but the implementation returned HTTP 404 for an unauthorized download.

**Correction and verification:** Updated the download test expectation to HTTP 404, which intentionally hides whether a private document exists. This verifies the expected response for that test; it does not, by itself, prove every route is secure. The latest verified combined test run passed 21 tests.

**Commit evidence:** See the [available TrustVault repository commit](https://github.com/shaikjohnbi/TrustVault/commit/f1ddb96). A separate historical commit for this step is not available.

## Entry 5 — 2026-10-22 — Security Threat Documentation

**Prompt recorded:** Help document TrustVault's security threats, mitigations, test coverage, and known limitations in `THREATS.md`.

**AI assistance:** Guidance for documenting unauthorized access, privilege escalation, permission revocation, malicious uploads, unauthorized permission changes, audit evidence, and input validation.

**Specific error:** No separate error record is available for this step.

**Correction and verification:** Created `THREATS.md`. The document must be checked against the actual implementation before submission; unimplemented controls must remain listed as limitations.

**Commit evidence:** See the [available TrustVault repository commit](https://github.com/shaikjohnbi/TrustVault/commit/f1ddb96). A separate historical commit for this step is not available.

## Review Checklist

- [ ] Verify that each prompt and AI-output description accurately represents the work performed.
- [ ] Add exact prompts or AI outputs only when supported by the actual development record.
- [ ] Do not invent historical commits, errors, or verification results.
- [ ] Create meaningful commits for future work as it is completed.
- [ ] Keep security limitations documented until the relevant controls are implemented and tested.
- [ ] Re-run `python manage.py test` before submission and update the verified result.
