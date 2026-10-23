# TrustVault — Secure Document Sharing with a Real Audit Trail

TrustVault is a Django-based document management and secure sharing application. It provides document ownership, permission-based access, private file downloads, and an audit trail for important activities.

## Features

- Upload and manage documents.
- Assign document owners.
- Grant or revoke per-document `READ` and `EDIT` permissions.
- Search and filter documents by title, owner, category, and date.
- Enforce server-side access control.
- Deny unauthorized document access and downloads.
- Validate uploaded files by extension, size, and file content.
- Record document activity and permission changes in an audit log.
- Run automated tests for authorization and audit behavior.

## Technology Stack

- Python
- Django
- Django REST Framework
- SQLite (development database)
- Pillow (image validation)

## Requirements

- Python compatible with the installed dependencies
- pip
- Git (recommended)

## Installation

Clone the repository and enter the project directory:

```bash
git clone YOUR_REPOSITORY_URL
cd TrustVault
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Apply database migrations:

```powershell
python manage.py migrate
```

Create an administrator account:

```powershell
python manage.py createsuperuser
```

Start the development server:

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Main Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/documents/` | List accessible documents and search/filter |
| POST | `/api/documents/upload/` | Upload a document |
| GET | `/api/documents/<id>/` | View document details |
| PATCH | `/api/documents/<id>/` | Update an editable document |
| DELETE | `/api/documents/<id>/` | Delete an editable document |
| GET | `/api/documents/<id>/grants/` | View grants as the owner |
| POST | `/api/documents/<id>/grants/` | Grant READ or EDIT access |
| DELETE | `/api/documents/<id>/grants/?grant_id=<grant_id>` | Revoke a grant |
| GET | `/api/documents/<id>/download/` | Download an authorized document |

## Authorization Model

- Document owners have full access to their own documents.
- Users with `READ` permission can view and download documents.
- Users with `EDIT` permission can read and modify documents.
- Only document owners can manage sharing grants.
- Access is checked on the server for document requests.
- Revoked grants should no longer authorize subsequent requests.

## Audit Trail

TrustVault records important events, including document uploads, views, downloads, updates, deletions, permission changes, and denied access attempts where implemented.

Audit events may contain the actor, document, action, outcome, IP address, timestamp, and additional details.

## Running Tests

Run the automated test suite:

```powershell
python manage.py test
```

## Security Notes

- Uploaded files are stored under the configured private media directory.
- Do not expose private document storage through a public static or media route.
- Use `DEBUG = False`, secure cookies, HTTPS, appropriate `ALLOWED_HOSTS`, and production-grade storage before deployment.
- Do not commit passwords, secret keys, database files containing real data, or private documents.
- File type validation is not a substitute for malware scanning.
- Review `THREATS.md` for threat scenarios, mitigations, tests, and accepted limitations.

## Project Documentation

- `THREATS.md` — security threats and mitigations.
- `PROMPTS.md` — AI-assisted development record.

## Current Development Status

The project has an automated test suite. Run the test command above and record the latest verified result before submitting.

## License

Add a license if you intend to distribute this project under specific reuse terms.
