# Oracle Fusion Access Manager – Step-by-Step Guide

This guide walks you through everything from installation to day-to-day usage
of the **Oracle Fusion Access Manager** desktop tool.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Install & Environment Setup](#2-install--environment-setup)
3. [Configure the Application](#3-configure-the-application)
4. [Generate Excel Templates](#4-generate-excel-templates)
5. [Launch the Application](#5-launch-the-application)
6. [Using the Application](#6-using-the-application)
   - 6.1 [User Management Tab](#61-user-management-tab)
   - 6.2 [Role Management Tab](#62-role-management-tab)
   - 6.3 [Data Access Tab](#63-data-access-tab)
   - 6.4 [Password Management Tab](#64-password-management-tab)
   - 6.5 [Security Analysis Tab](#65-security-analysis-tab)
   - 6.6 [Audit & Reporting Tab](#66-audit--reporting-tab)
   - 6.7 [Job Monitor Tab](#67-job-monitor-tab)
7. [Bulk User Upload (Excel)](#7-bulk-user-upload-excel)
8. [Exporting Reports](#8-exporting-reports)
9. [Running Tests](#9-running-tests)
10. [Build a Windows EXE](#10-build-a-windows-exe)
11. [Create an Installer Package](#11-create-an-installer-package)
12. [Credential & Security Best Practices](#12-credential--security-best-practices)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Prerequisites

Before you begin, make sure the following are installed on your machine:

| Requirement | Minimum version | Notes |
|---|---|---|
| Python | 3.11 or 3.12 | Windows recommended for full feature support |
| Git | Any recent version | For cloning the repository |
| pip | Bundled with Python | Used to install dependencies |
| Inno Setup *(optional)* | 6.x | Only needed to build the installer `.exe` |

> **Windows users:** Make sure Python is added to your `PATH` during
> installation (tick "Add Python to PATH" in the installer).

---

## 2. Install & Environment Setup

### Step 1 – Clone the repository

```bash
git clone https://github.com/iamarunshetty/Oracle-Cloud-Autonomous-tool.git
cd Oracle-Cloud-Autonomous-tool
```

### Step 2 – Create a virtual environment

```bash
python -m venv .venv
```

### Step 3 – Activate the virtual environment

**Windows (Command Prompt / PowerShell):**

```cmd
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

### Step 4 – Install all dependencies

```bash
pip install -r requirements.txt
```

Or use the Makefile shortcut:

```bash
make install
```

---

## 3. Configure the Application

### Step 5 – Copy the example environment file

```bash
cp .env.example .env
```

On Windows:

```cmd
copy .env.example .env
```

### Step 6 – Edit `.env` with your Oracle Fusion details

Open `.env` in any text editor and set your values:

```env
# Your Oracle Fusion Cloud tenant base URL (required)
FUSION_BASE_URL=https://your-tenant.oraclecloud.com

# Credentials – leave blank here; use the secrets provider instead (see step 7)
FUSION_USERNAME=
FUSION_PASSWORD=

# Path to the local SQLite database (default is fine for most users)
DB_PATH=fusion_tool.db

# Logging verbosity: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

> **Important:** Never commit the `.env` file. It is already in `.gitignore`.

### Step 7 – Store credentials securely

By default the app reads `FUSION_USERNAME` and `FUSION_PASSWORD` from
environment variables via `app/security/secrets_provider.py`.

**Option A – Environment variables (default, cross-platform):**

Set the variables in your shell before running:

```bash
export FUSION_USERNAME=your_username
export FUSION_PASSWORD=your_password
```

**Option B – Windows Credential Manager (recommended for Windows):**

1. Install `pywin32`:

   ```bash
   pip install pywin32
   ```

2. Open `app/security/secrets_provider.py` and uncomment the
   `WindowsCredentialProvider` class.
3. Change the last line to:

   ```python
   secrets: SecretsProvider = WindowsCredentialProvider()
   ```

4. Store your credentials once via Windows Credential Manager UI or via
   the `set_credential` method.

---

## 4. Generate Excel Templates

### Step 8 – Create the bulk-upload Excel template

Run this once before first use (or whenever you want a fresh template):

```bash
python -m app.services.template_generator
```

Or via Make:

```bash
make templates
```

This creates `templates/bulk_user_upload_template.xlsx`, which you will fill
in when doing bulk user uploads (see [Section 7](#7-bulk-user-upload-excel)).

---

## 5. Launch the Application

### Step 9 – Start the desktop application

```bash
python main.py
```

Or via Make:

```bash
make run
```

On first launch, the app automatically creates `fusion_tool.db` (SQLite
database) in the project root for audit trail and job history storage.

The main window opens with **seven functional tabs** across the top.

---

## 6. Using the Application

### 6.1 User Management Tab

Manage Oracle Fusion user accounts.

| Action | How to use |
|---|---|
| **Search users** | Enter a username or partial name → click **Search** |
| **Create user** | Click **New User** → fill in the form → click **Create** |
| **Edit user** | Select a user from the list → click **Edit** → update fields → **Save** |
| **Enable / Disable** | Select a user → click **Enable** or **Disable** |
| **Delete / Terminate** | Select a user → click **Delete** → confirm the dialog |
| **Compare users** | Select two users → click **Compare** to see a side-by-side diff |
| **Bulk upload** | Click **Bulk Upload** → browse for your filled-in Excel file → **Upload** |

### 6.2 Role Management Tab

Manage role assignments for users.

| Action | How to use |
|---|---|
| **Assign role** | Select a user → select a role from the list → click **Assign** |
| **Remove role** | Select a user → select an assigned role → click **Remove** |
| **Copy roles** | Select source user and target user → click **Copy Roles A → B** |
| **Compare roles** | Select two users → click **Compare Roles** |
| **Request approval** | Select a role → click **Request Approval** → fill in justification |
| **View history** | Select a user → click **Role History** to see past assignments |

### 6.3 Data Access Tab

Manage data roles and security contexts.

| Action | How to use |
|---|---|
| **Assign data role** | Select a user → select a data role → click **Assign** |
| **Assign security context** | Select a user → define the context values → **Assign** |
| **Compare data access** | Select two users → click **Compare** |

### 6.4 Password Management Tab

Manage passwords and account lock status.

| Action | How to use |
|---|---|
| **Reset password** | Search for a user → click **Reset Password** → confirm |
| **Force password change** | Search for a user → click **Force Change** |
| **Unlock account** | Search for a user → click **Unlock** |
| **View login status** | Search for a user → click **Login Status** to see last login info |

### 6.5 Security Analysis Tab

Detect access control issues.

| Action | How to use |
|---|---|
| **SoD check** | Click **Run SoD Check** → review the conflicts listed |
| **Elevated access** | Click **Detect Elevated Access** → review flagged users |
| **Inactive users** | Click **Inactive Users** → set inactivity threshold in days → **Run** |
| **Orphan roles** | Click **Orphan Roles** → review roles with no active assignments |
| **Duplicate access** | Click **Duplicate Access** → review users with duplicate role sets |

### 6.6 Audit & Reporting Tab

View the audit trail and export reports.

| Action | How to use |
|---|---|
| **View audit trail** | Filter by date range or user → click **Search** |
| **Export to Excel** | Click **Export Excel** → choose save location |
| **Export to PDF** | Click **Export PDF** → choose save location |
| **Export to CSV** | Click **Export CSV** → choose save location |

### 6.7 Job Monitor Tab

Track the status of background operations.

| Action | How to use |
|---|---|
| **View jobs** | Jobs are listed automatically with status (Pending / Running / Done / Failed) |
| **Refresh** | Click **Refresh** to update the job list |
| **View details** | Select a job → click **Details** for full output |

---

## 7. Bulk User Upload (Excel)

### Step 10 – Prepare the upload file

1. Open `templates/bulk_user_upload_template.xlsx`.
2. Fill in one row per user. Required columns:
   - `username`
   - `first_name`
   - `last_name`
   - `email`
   - `roles` *(comma-separated role names)*
3. Save the file.

### Step 11 – Upload the file

1. Navigate to the **User Management** tab.
2. Click **Bulk Upload**.
3. Browse to your saved Excel file → click **Open**.
4. Review the validation summary shown in the log panel.
5. Rows that pass validation are queued for processing; failed rows are
   highlighted with the reason.

---

## 8. Exporting Reports

### Step 12 – Generate a report

1. Go to the **Audit & Reporting** tab.
2. Apply any filters (date range, user, action type).
3. Choose an export format:
   - **Export Excel** → saves as `.xlsx`
   - **Export PDF** → saves as `.pdf`
   - **Export CSV** → saves as `.csv`
4. Select the output directory and filename → click **Save**.

Reports are generated locally from the SQLite audit database and do not
require a live Oracle Fusion connection.

---

## 9. Running Tests

### Step 13 – Execute the test suite

```bash
pytest tests/ -v
```

Or via Make:

```bash
make test
```

The test suite covers:

| Test file | What it tests |
|---|---|
| `tests/test_config.py` | Settings loading from environment variables |
| `tests/test_bulk_upload.py` | Excel validation logic |
| `tests/test_audit_trail.py` | Audit event write path (SQLite) |
| `tests/test_report_export.py` | Excel/PDF/CSV report generation |

---

## 10. Build a Windows EXE

### Step 14 – Install PyInstaller

```bash
pip install pyinstaller
```

### Step 15 – Build the executable

```bash
pyinstaller --noconfirm FusionAccessManager.spec
```

Or via Make:

```bash
make build-exe
```

The output executable is placed at:

```
dist/FusionAccessManager.exe
```

> **Tip:** To set a custom icon, edit the `icon=` line in
> `FusionAccessManager.spec` to point to your `.ico` file before building.

---

## 11. Create an Installer Package

> **Windows only.** Requires [Inno Setup](https://jrsoftware.org/isinfo.php).

### Step 16 – Build the EXE first

Complete [Section 10](#10-build-a-windows-exe) before proceeding.

### Step 17 – Run Inno Setup Compiler

```cmd
ISCC installer.iss
```

The installer `FusionAccessManagerSetup.exe` is created in the project root.
It bundles:
- `dist/FusionAccessManager.exe`
- `.env.example`
- `templates/bulk_user_upload_template.xlsx`

---

## 12. Credential & Security Best Practices

| Rule | Details |
|---|---|
| **Never commit `.env`** | It is in `.gitignore`; double-check before every push |
| **Use least-privilege accounts** | Run the app with a Windows user that has only necessary Oracle Fusion permissions |
| **Prefer Windows Credential Manager** | More secure than plain environment variables on Windows (see [Step 7](#step-7--store-credentials-securely)) |
| **Audit trail** | Every UI action is recorded in `fusion_tool.db` → `audit_events` table |
| **Rotate credentials regularly** | If you suspect exposure, rotate your Oracle Fusion API credentials immediately |

---

## 13. Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `PySide6 is required` error on startup | PySide6 not installed | Run `pip install -r requirements.txt` |
| `FUSION_BASE_URL` not set warning | `.env` missing or not loaded | Run `cp .env.example .env` and set `FUSION_BASE_URL` |
| `fusion_tool.db` permission error | DB file locked by another process | Close any other running instances of the tool |
| Excel template not found | Template not generated | Run `python -m app.services.template_generator` |
| Bulk upload validation errors | Data does not match expected columns | Re-download the template and follow the column format exactly |
| EXE build fails | PyInstaller not installed | Run `pip install pyinstaller` first |
| Tests fail with import errors | Virtual environment not activated | Activate `.venv` and re-run `pip install -r requirements.txt` |
| UI does not appear (headless CI) | No display available | Set `QT_QPA_PLATFORM=offscreen` environment variable |

---

> **Need help?** Open an issue at
> [github.com/iamarunshetty/Oracle-Cloud-Autonomous-tool/issues](https://github.com/iamarunshetty/Oracle-Cloud-Autonomous-tool/issues).
