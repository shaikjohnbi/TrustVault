# TrustVault — Secure Document Sharing with a Real Audit Trail

TrustVault is a Django-based document management and secure sharing application. It provides document ownership, permission-based sharing, private file downloads, and audit logging.

## Features

- Upload and manage documents.
- Assign document owners.
- Grant and revoke per-document `READ` and `EDIT` permissions.
- Restrict document access according to user permissions.
- Download documents through an authorized server endpoint.
- Search and filter documents by title, owner, category, and date.
- Validate uploaded files by extension, size, and file content.
- Record document activity and permission changes in an audit trail.
- Record relevant denied-access attempts where implemented.
- Manage users, documents, permissions, and audit events through Django administration.
- Run automated tests for authorization and audit behavior.

## Live Application

- **Website:** https://trustvault-lmf5.onrender.com/
- **Admin dashboard:** https://trustvault-lmf5.onrender.com/admin/
- **Documents API:** https://trustvault-lmf5.onrender.com/api/documents/
- **GitHub repository:** https://github.com/shaikjohnbi/TrustVault

The application is deployed on Render. The documents API may return an empty collection when no documents are available to the requesting user.

## Technology Stack

- Python
- Django
- Django REST Framework
- SQLite for local development
- PostgreSQL when configured for deployment
- Pillow for image validation
- Gunicorn for production serving
- WhiteNoise for static files
- dj-database-url for database configuration

## Project Structure

```text
TrustVault/
├── audit/
├── config/
├── documents/
├── PROMPTS.md
├── THREATS.md
├── requirements.txt
├── .env.example
├── .gitignore
├── manage.py
└── README.md
```

The `documents` application manages documents and sharing permissions. The `audit` application manages audit events. The `config` directory contains the Django project configuration.

## Requirements

- Python compatible with the pinned dependencies
- pip
- Git
- Windows PowerShell or another terminal
- PostgreSQL for deployments configured to use PostgreSQL

## Installation and Local Setup

### 1. Clone the repository

```powershell
git clone https://github.com/shaikjohnbi/TrustVault.git
cd TrustVault
```

If you already have the repository, open its existing directory instead of cloning it again.

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Use `.env.example` as a reference. Django does not automatically load `.env` unless a compatible loader is configured.

For local development, set environment variables in PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = "replace-with-a-unique-development-secret"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
```

Use a unique secret for local development. Never commit production secrets, passwords, or database credentials to GitHub.

### 5. Apply database migrations

```powershell
python manage.py migrate
```

### 6. Create an administrator account

```powershell
python manage.py createsuperuser
```

Follow the prompts to create the administrator username and password.

### 7. Start the development server

```powershell
python manage.py runserver
```

Open these addresses in your browser:

- Website: http://127.0.0.1:8000/
- Admin dashboard: http://127.0.0.1:8000/admin/
- Documents API: http://127.0.0.1:8000/api/documents/

## API Endpoints

The following table documents the intended API interface. Confirm request formats and behavior against the current implementation before integrating with these endpoints.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/documents/` | List accessible documents and search/filter |
| POST | `/api/documents/upload/` | Upload a document |
| GET | `/api/documents/<id>/` | Retrieve document details |
| PATCH | `/api/documents/<id>/` | Update an editable document |
| DELETE | `/api/documents/<id>/` | Delete an authorized document |
| GET | `/api/documents/<id>/grants/` | View sharing grants as the owner |
| POST | `/api/documents/<id>/grants/` | Grant READ or EDIT access |
| DELETE | `/api/documents/<id>/grants/?grant_id=<grant_id>` | Revoke a sharing grant |
| GET | `/api/documents/<id>/download/` | Download an authorized document |

## Authorization Model

TrustVault uses document ownership and per-document sharing permissions.

- **Owner:** Has access to their own document according to the implemented authorization rules.
- **READ permission:** Allows an authorized user to read and download a shared document.
- **EDIT permission:** Allows an authorized user to read and modify a shared document.
- **Grant management:** Only the document owner should be allowed to manage sharing permissions.
- **Revocation:** Revoking a grant should prevent subsequent requests from using that grant to access the document.
- **Server-side authorization:** Protected operations must check permissions on the server rather than relying only on interface restrictions.

Unauthorized requests should not expose private document contents or file locations.

## File Validation and Storage

The current file-validation rules accept these extensions:

- PDF
- TXT
- PNG
- JPG and JPEG
- DOCX

The configured maximum upload size is 10 MB.

Validation includes extension and content checks, with Pillow used for image validation. These checks reduce certain invalid uploads but do not guarantee that a file is safe.

Production deployments should ensure that:

- Private documents are not served from publicly accessible static or media directories.
- Downloads pass through authorization checks.
- File storage permissions prevent unauthorized direct access.
- Upload size limits are enforced.
- Malware scanning and additional file-content validation are considered where appropriate.

## Audit Trail

The audit application records security-relevant document activity where implemented, including applicable upload, download, update, deletion, permission-change, and denied-access events.

Depending on the event and implementation, an audit record may contain the actor, document, action, outcome, IP address, timestamp, and additional details.

Audit logs should be reviewed to confirm that important actions are recorded correctly. An empty audit-events page does not by itself prove that the audit system is broken or that all audit scenarios work.

## Automated Testing

Run the test suite from the project directory with the virtual environment activated:

```powershell
python manage.py test
```

Run the tests against the latest code and record the actual result before submitting.

Important scenarios to verify include:

- Owners accessing their own documents.
- Users without permission being denied access.
- READ users being prevented from editing documents.
- EDIT users modifying authorized documents.
- Owners granting and revoking permissions.
- Revoked users losing access on subsequent requests.
- Unauthorized downloads being denied.
- Relevant actions and denied attempts being recorded in the audit trail.

## Deployment

TrustVault is deployed on Render.

**Live URL:** https://trustvault-lmf5.onrender.com/

The deployment uses environment variables for configuration and a database URL for database selection.

Typical production environment variables include:

- `DJANGO_SECRET_KEY` — a securely generated secret key.
- `DJANGO_DEBUG=False` — disables Django debug mode.
- `DJANGO_ALLOWED_HOSTS` — permitted hostnames.
- `DJANGO_CSRF_TRUSTED_ORIGINS` — trusted origins.
- `DATABASE_URL` — the deployment database connection URL.
- `BOOTSTRAP_ADMIN_USERNAME` — the configured deployment administrator username.
- `BOOTSTRAP_ADMIN_PASSWORD` — the configured deployment administrator password.

Never publish the values of these variables.

After deployment, verify migrations, authentication, document storage, authorization, and audit logging using the live application.

## Security Considerations

- Keep production secrets and database credentials out of source control.
- Use HTTPS and appropriate secure cookie settings in production.
- Set `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS` and CSRF trusted origins correctly.
- Keep private documents outside public static-file serving paths.
- Enforce authorization on every protected document operation.
- Avoid exposing sensitive details in error responses.
- Review audit coverage and access-control tests.
- Remember that file extension checks do not replace malware scanning.
- Review `THREATS.md` for threat scenarios, mitigations, tests, and accepted limitations.

## Project Documentation

- `README.md` — project overview, installation, API, testing, and deployment.
- `THREATS.md` — threat scenarios, mitigations, and security limitations.
- `PROMPTS.md` — AI-assisted development record, prompts, errors, and corrections.

## Current Status

The application has been deployed to Render, and the Django administration interface is accessible.

Before claiming that every feature is fully verified, run the automated tests and check the live upload, download, sharing, permission-revocation, and audit workflows.

## License

No license has been specified. Add a suitable license if you intend to distribute the project under explicit reuse terms.
