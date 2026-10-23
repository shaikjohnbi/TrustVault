# TrustVault — Threat Model

## 1. Purpose and Scope

TrustVault is a secure document-sharing application built with Django. It supports document ownership, per-document READ and EDIT permissions, file uploads and downloads, and audit events.

This document identifies security threats, the controls currently implemented, the tests used to verify them, and known limitations that require further work.

## 2. Assets to Protect

- Uploaded document contents and files.
- Document titles, descriptions, categories, and metadata.
- User accounts and authentication sessions.
- Document ownership and sharing permissions.
- Audit events containing user actions and access-denial records.
- The database and private file storage.

## 3. Threat Actors

- An unauthenticated visitor attempting to access private documents.
- An authenticated user attempting to access another user's documents without permission.
- A viewer attempting to modify or delete a document.
- A user attempting to manage permissions for a document they do not own.
- A malicious user uploading an unexpected or harmful file.
- An administrator or attacker with access to the application server or database.

## 4. Threat Scenarios and Mitigations

### Threat 1: Unauthorized Document Access

**Attack:** A user guesses a document ID and requests its details or download URL.

**Potential impact:** Confidential documents may be exposed.

**Implemented controls:**
- Document detail and download endpoints require authentication.
- Access is checked against ownership and document grants.
- Unauthorized detail and download attempts return HTTP 403.
- Automated tests check denial of access for users without grants.

**Verification:** `documents/tests.py`, including the ungranted-user detail and download tests.

### Threat 2: Privilege Escalation

**Attack:** A user with READ permission attempts to update or delete a document, or a non-owner attempts to change sharing permissions.

**Potential impact:** Unauthorized changes, deletion, or disclosure.

**Implemented controls:**
- READ and EDIT permissions are checked separately.
- READ grants permit reading but not editing.
- Permission management is restricted to the document owner.
- Automated tests cover READ/EDIT authorization behavior.

**Verification:** `documents/tests.py` and `audit/tests.py`.

### Threat 3: Access After Permission Revocation

**Attack:** A user continues to access a document after the owner revokes their grant.

**Potential impact:** Continued unauthorized access to confidential files.

**Implemented controls:**
- Document access checks query the current grant records.
- Revoking a grant deletes its database record.
- An automated test verifies that access is denied after the grant is deleted.

**Verification:** `test_revoked_grant_removes_access_immediately` in `documents/tests.py`.

**Limitation:** Previously downloaded copies cannot be recalled. Already-open file handles or data previously delivered to a client may remain accessible.

### Threat 4: Malicious or Invalid File Uploads

**Attack:** A user uploads an empty, oversized, or disallowed-extension file.

**Potential impact:** Storage exhaustion, unsafe file handling, or attempts to introduce harmful content.

**Implemented controls:**
- Uploads require authentication.
- A title and file are required.
- Empty files are rejected.
- The maximum accepted file size is 10 MB.
- File extensions are restricted to PDF, TXT, PNG, JPG, JPEG, and DOCX.
- Storage errors are handled without returning internal exception details.

**Known limitation:** Extension checks alone do not verify the true file format or content. MIME/content-signature validation, malware scanning, and production-grade upload controls remain necessary.

### Threat 5: Unauthorized Permission Changes

**Attack:** A non-owner attempts to grant, change, or revoke another user's document access.

**Potential impact:** Unintended disclosure or loss of document access.

**Implemented controls:**
- Only the owner can manage document grants.
- Grant permissions are restricted to READ or EDIT.
- Duplicate document-user grants are prevented by a database uniqueness constraint.
- Successful grant and revoke operations create audit events.

**Verification:** Permission grant and revoke route tests in `audit/tests.py`.

### Threat 6: Missing Audit Evidence

**Attack:** A user performs sensitive actions or repeatedly attempts denied access, but the activity is not recorded.

**Potential impact:** Reduced accountability and difficulty investigating incidents.

**Implemented controls:**
- Audit events record an actor, action, outcome, optional document, IP address, details, and timestamp.
- Upload, download, document modification, and permission-management code paths include audit logging.
- Denied detail, download, and permission-management attempts are logged.
- Automated tests verify audit event creation and permission grant/revoke logging.

**Known limitation:** Application-level audit events are stored in the same database as the application. A privileged database operator could modify or delete them. The current design is not a tamper-proof or cryptographically signed audit system.

### Threat 7: Malformed Input

**Attack:** A user sends malformed JSON, unsupported fields, invalid permissions, or invalid document metadata.

**Potential impact:** Incorrect state changes, unexpected errors, or abuse of API endpoints.

**Implemented controls:**
- JSON parsing errors are handled.
- Unsupported update fields and invalid permission values are rejected.
- Document titles and uploaded file requirements are validated.

**Known limitation:** Additional boundary-value tests and stronger validation should be added before production deployment.

## 5. Security Test Coverage

The current automated test suites include:

- `documents/tests.py`: 7 tests for owner access, unauthorized access, READ/EDIT behavior, revocation, and detail/download authorization.
- `audit/tests.py`: 6 tests for audit event creation, denied outcomes, unauthenticated actors, event ordering, and permission grant/revoke audit records.

Both test suites passed during development. Passing these tests does not prove that every attack path is secure. Additional endpoint, upload-validation, authentication, and deployment tests are still required.

## 6. Accepted Limitations and Future Work

Before production deployment, the following should be addressed:

1. Validate uploaded file content, not just its extension.
2. Verify that private files cannot be accessed through a public static or media URL.
3. Add automated tests for upload validation, update/delete auditing, and denied permission-management attempts.
4. Review session security, CSRF protection, password policy, and rate limiting.
5. Protect audit records against unauthorized modification and define a retention policy.
6. Use HTTPS, secure production settings, protected secrets, and a production-grade database and file-storage configuration.
7. Review dependencies and apply security updates.
8. Test the application as multiple distinct users, including revoked and expired access scenarios.

## 7. Security Principle

TrustVault follows the principle of least privilege: users should receive only the document permissions they need. Authorization must be enforced on the server for every protected request, rather than relying on hidden buttons or frontend behavior.

This threat model should be updated whenever authentication, storage, permissions, or document endpoints change.