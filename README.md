# Oracle Fusion User Administration Tool

A production-ready **desktop application** for Oracle Fusion IAM / user-management tasks, built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

📖 **[User Guide](docs/user_guide.md)** – step-by-step instructions for every feature of the app.

---

## Features

| Module | Description |
|---|---|
| **Create User** | Create a new Oracle Fusion user account with validation |
| **Update User** | Look up a user by ID and update profile fields |
| **Lock / Unlock** | Lock or unlock a user account with confirmation prompt |
| **Role Management** | View, assign, and remove roles for any user |
| **Audit Log** | In-app log of all operations; one-click CSV export |
| **Settings** | Configure connection details at runtime (session-only) |

---

## Project Structure

```
Oracle-Cloud-Autonomous-tool/
├── main.py                      # Entry point
├── requirements.txt
├── .env.example                 # Environment variable template
├── config.example.json          # JSON config template
├── app/
│   ├── config.py                # Configuration (env vars + config.json)
│   ├── api/
│   │   ├── client.py            # HTTP client (auth, retry, error mapping)
│   │   └── endpoints.py         # Oracle Fusion REST endpoint paths
│   ├── services/
│   │   ├── user_service.py      # User CRUD + lock/unlock
│   │   ├── role_service.py      # Role assignment / removal
│   │   └── audit_service.py     # Audit log + CSV persistence
│   ├── ui/
│   │   ├── app_window.py        # Main window + sidebar navigation
│   │   ├── create_user.py       # Create User panel
│   │   ├── update_user.py       # Update User panel
│   │   ├── lock_unlock.py       # Lock/Unlock panel
│   │   ├── role_management.py   # Role Management panel
│   │   ├── audit_panel.py       # Audit Log panel
│   │   ├── settings_panel.py    # Connection Settings panel
│   │   └── widgets.py           # Reusable UI components
│   └── utils/
│       ├── validators.py        # Form-field validation helpers
│       └── logger.py            # Structured logger with secret masking
└── tests/
    ├── test_validators.py
    ├── test_api_client.py
    └── test_audit_service.py
```

---

## Setup

### Prerequisites

- Python 3.10 or later  
- `pip`  
- Windows is the primary target; macOS and Linux are also supported

### Install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Configuration

The app reads credentials from **environment variables** (recommended) or a local `config.json`.  
**Never commit real credentials to source control.**

### Option A – Environment variables / `.env` file

```bash
cp .env.example .env
# Edit .env and fill in your values
```

Key variables:

| Variable | Description | Default |
|---|---|---|
| `ORACLE_BASE_URL` | Oracle Fusion base URL | _(required)_ |
| `ORACLE_USERNAME` | Admin username (basic auth) | |
| `ORACLE_PASSWORD` | Admin password (basic auth) | |
| `ORACLE_TOKEN` | Bearer token (overrides basic auth) | |
| `ORACLE_REQUEST_TIMEOUT` | Per-request timeout in seconds | `30` |
| `ORACLE_RETRY_COUNT` | Max retries for transient failures | `3` |
| `APP_LOG_LEVEL` | Log level (`DEBUG`, `INFO`, `WARNING`) | `INFO` |

### Option B – `config.json`

```bash
cp config.example.json config.json
# Edit config.json and fill in your values
```

> **Tip:** Settings can also be entered or overridden at runtime via the **Settings** panel inside the app (session-only; not persisted to disk).

---

## Running the App

```bash
python main.py
```

On first launch the app opens with no connection configured; navigate to **Settings** (bottom of the sidebar) to enter your Oracle Fusion URL and credentials before using the other modules.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

Tests cover:
- Form validation helpers (`test_validators.py`)
- API client error handling and retry logic (`test_api_client.py`)
- Audit service recording and CSV export (`test_audit_service.py`)

No live Oracle Fusion connection is required; all HTTP calls are mocked with the `responses` library.

---

## Security

- Credentials are **never hardcoded** – only environment variables or the local (gitignored) `config.json`.
- The structured logger automatically masks `password`, `token`, and `Authorization` header values in log output.
- Destructive actions (lock, unlock, role removal) require an explicit confirmation dialog.

---

## Architecture Notes

### API Client (`app/api/client.py`)

The `OracleAPIClient` is a pluggable HTTP adapter:
- Supports basic auth and bearer-token auth.
- Retries transient errors (429, 5xx) with exponential back-off.
- Maps HTTP status codes to human-readable error messages shown in the UI.
- All endpoint paths live in `app/api/endpoints.py` – updating Oracle Fusion API paths requires no UI changes.

### Service Layer (`app/services/`)

A thin service layer sits between the UI and the API client, translating Oracle Fusion REST payloads into simple Python dicts and raising `APIError` on failure. The UI only depends on the service interfaces, so endpoint implementations can be swapped or mocked freely.

### Audit Log

Every user-initiated action is recorded (timestamp, action type, target user, result, message) both in memory and appended to `audit_log.csv`. The **Audit Log** panel lets you review and export all entries.

---

## Known Limitations & Next Steps

| Limitation | Notes |
|---|---|
| No live Oracle Fusion instance in CI | All tests mock HTTP; verify against a real sandbox before production use |
| Basic auth only for OAuth 2.0 flows | Extend `OracleAPIClient` with an OAuth 2.0 / SAML token-refresh flow |
| User search uses simple `LIKE` query | Add paginated search with server-side filtering when working against large directories |
| Role list is fetched on-demand | Cache role list with a TTL for better performance |
| No installer / packaging | Bundle with PyInstaller or cx_Freeze for a standalone `.exe` on Windows |
| Audit log is local only | Optionally stream audit entries to a centralised logging system (Splunk, ELK, etc.) |

---

## License

This project is provided as-is for internal use. Contact the repository owner for licensing questions.

