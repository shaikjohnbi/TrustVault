# AI Prompt and Engineering Log — TrustVault

**Project:** TrustVault — Secure Document Sharing with a Real Audit Trail  
**Purpose:** Record AI-assisted development, validation, errors, corrections, and related commits.

> Transparency note: This log must reflect work actually performed. Replace any placeholders with the exact prompt, output, error, correction, and real commit URL from your development history. Do not invent errors or commit links.

## Entry 1 — 2026-10-22 — Document Authorization

**Prompt:** Help me implement and test document access rules so that owners have full access, users with READ grants can only read, and users with EDIT grants can read and edit.

**AI output:** Guidance for a centralized `can_access_document()` permission helper and automated permission tests.

**Specific error encountered:** No error recorded for this step.

**Correction and verification:** Created tests for owner access, ungranted users, READ grants, and EDIT grants. The document permission test suite passed 7 tests.

**Commit link:** TODO — add the real Git commit URL after committing this work.

## Entry 2 — 2026-10-22 — Immediate Permission Revocation

**Prompt:** Help me verify that a user's access is denied immediately after their document grant is revoked.

**AI output:** Guidance for testing access before and after deleting a `DocumentGrant`.

**Specific error encountered:** No error recorded for this step.

**Correction and verification:** Added a test that confirms access is allowed before revocation and denied after the grant is deleted. The document permission test suite passed.

**Commit link:** TODO — add the real Git commit URL after committing this work.

## Entry 3 — 2026-10-22 — Audit Trail

**Prompt:** Help me test the audit event service for successful actions, denied access, anonymous actors, and event ordering.

**AI output:** Guidance for tests covering audit event fields, denied outcomes, missing actors, and newest-first ordering.

**Specific error encountered:** No error recorded for this step.

**Correction and verification:** Added audit service tests. The audit test suite passed 6 tests, including permission grant and revocation audit tests.

**Commit link:** TODO — add the real Git commit URL after committing this work.

## Entry 4 — 2026-10-22 — Unauthorized Document Routes

**Prompt:** Help me test that an ungranted user cannot view or download another user's private document.

**AI output:** Guidance for Django client tests that authenticate as an unrelated user and request document detail and download endpoints.

**Specific error encountered:** No error recorded for this step.

**Correction and verification:** Added route-level authorization tests. The document test suite passed 7 tests.

**Commit link:** TODO — add the real Git commit URL after committing this work.

## Entry 5 — 2026-10-22 — Security Threat Documentation

**Prompt:** Help me document TrustVault's security threats, mitigations, test coverage, and known limitations in THREATS.md.

**AI output:** A threat-model document covering unauthorized access, privilege escalation, permission revocation, malicious uploads, permission changes, audit evidence, and input validation.

**Specific error encountered:** No error recorded for this step.

**Correction and verification:** Created `THREATS.md`. Review each listed control and limitation against the actual implementation before submission; do not claim unverified protections.

**Commit link:** TODO — add the real Git commit URL after committing this work.

## Review Checklist

- [ ] Verify every entry matches the actual development history.
- [ ] Add genuine errors and their corrections when they occur; do not invent them.
- [ ] Add a real commit URL for each entry, or clearly link entries to the actual commit that contains the work.
- [ ] Update this log as development continues.
- [ ] Keep known security limitations documented until they are actually fixed and tested.