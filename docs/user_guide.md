# Oracle Fusion User Administration Tool – User Guide

This guide explains how to install, configure, and use every feature of the **Oracle Fusion User Administration** desktop application.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Launching the App](#4-launching-the-app)
5. [Interface Layout](#5-interface-layout)
6. [Settings](#6-settings)
7. [Create User](#7-create-user)
8. [Update User](#8-update-user)
9. [Lock / Unlock User](#9-lock--unlock-user)
10. [Role Management](#10-role-management)
11. [Audit Log](#11-audit-log)
12. [Tips & Troubleshooting](#12-tips--troubleshooting)

---

## 1. Overview

The Oracle Fusion User Administration Tool is a desktop application for managing Oracle Fusion Cloud user accounts. It provides a graphical interface for the following tasks without needing to navigate the Oracle Fusion web console:

| Module | What it does |
|---|---|
| **Settings** | Enter or override your Oracle Fusion connection details |
| **Create User** | Create a new Oracle Fusion user account |
| **Update User** | Look up a user by ID and edit their profile |
| **Lock / Unlock** | Immediately lock or unlock a user's account |
| **Role Management** | View, assign, and remove roles for a user |
| **Audit Log** | Review all actions performed in this session and export as CSV |

---

## 2. Installation

### Prerequisites

- **Python 3.10 or later** installed and on your `PATH`
- `pip` (bundled with Python)
- Windows (primary target); macOS and Linux are also supported

### Steps

1. Download or clone the repository.

2. Open a terminal in the project directory and create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:

   ```bash
   # Windows
   .venv\Scripts\activate

   # macOS / Linux
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 3. Configuration

The app needs a **Base URL** and credentials to communicate with your Oracle Fusion instance. You can supply these before launching (recommended for daily use) or enter them inside the app after launch.

### Option A – `.env` file (recommended)

1. Copy the template:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` in a text editor and fill in your values:

   ```ini
   ORACLE_BASE_URL=https://your-instance.oraclecloud.com
   ORACLE_USERNAME=your_admin_username
   ORACLE_PASSWORD=your_admin_password
   ```

   If you use a ****** instead of basic auth, set `ORACLE_TOKEN` and leave the username/password blank.

3. Save the file. The app reads it automatically on startup.

> **Important:** Never commit `.env` to source control. It is already listed in `.gitignore`.

### Option B – `config.json`

1. Copy the template:

   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` with your Oracle Fusion details and save.

### Option C – Inside the app (session only)

Use the **Settings** panel (see [Section 6](#6-settings)). Values entered there apply for the current session only and are not saved to disk.

---

## 4. Launching the App

With the virtual environment active, run:

```bash
python main.py
```

The app window opens at **1050 × 700 pixels** (resizable; minimum 900 × 600). If you have not configured credentials yet, the status indicator at the bottom of the sidebar shows **"⬤ Not connected"**.

---

## 5. Interface Layout

```
┌──────────────┬──────────────────────────────────┐
│  Sidebar     │  Content area                    │
│              │                                  │
│  Oracle      │  (active module is shown here)   │
│  Fusion      │                                  │
│              │                                  │
│  ➕ Create   │                                  │
│  ✏ Update   │                                  │
│  🔒 Lock     │                                  │
│  🛡 Roles    │                                  │
│  📋 Audit    │                                  │
│  ⚙ Settings │                                  │
│              │                                  │
│  ⬤ status   │                                  │
└──────────────┴──────────────────────────────────┘
```

- **Sidebar** – click any navigation item to switch modules. The active item is highlighted.
- **Content area** – displays the form or table for the selected module.
- **Connection status** (bottom-left) – shows the Base URL when connected, or "Not connected" otherwise.

---

## 6. Settings

> **Start here** if you have not configured credentials yet, or when you need to connect to a different Oracle Fusion instance.

### How to open

Click **⚙ Settings** in the sidebar.

### Fields

| Field | Required | Description |
|---|---|---|
| **Base URL** | ✅ | Your Oracle Fusion instance URL (e.g. `https://xyz.oraclecloud.com`) |
| **Username** | Basic auth | Admin username for basic authentication |
| **Password** | Basic auth | Admin password (masked on screen) |
| ******** | Token auth | If provided, overrides username/password |
| **Timeout (s)** | | Per-request timeout in seconds (default: 30) |
| **Retry Count** | | Number of retries for transient failures (default: 3) |

### Applying settings

1. Fill in the required fields.
2. Click **Apply Settings**.
3. A green confirmation message appears and the sidebar status updates to show the Base URL.

### Resetting to defaults

Click **Reset to Env Defaults** to reload values from your `.env` or `config.json` file, discarding any in-session changes.

> **Note:** Settings entered here are kept in memory for the current session only. They are not written to any file on disk.

---

## 7. Create User

### How to open

Click **➕ Create User** in the sidebar.

### Steps

1. Fill in the form fields:

   | Field | Required | Notes |
   |---|---|---|
   | **Username** | ✅ | Must be unique in Oracle Fusion |
   | **First Name** | ✅ | |
   | **Last Name** | ✅ | |
   | **Work Email** | ✅ | Must be a valid email address |
   | **Description** | | Optional free-text note |

2. Click **Create User**.
   - If any field fails validation, an error message appears beneath the form listing the specific issues.
   - On success, a green confirmation message is shown and the form is cleared automatically.

3. To discard the current input without submitting, click **Clear**.

### Validation rules

- **Username** – must not be empty; only valid identifier characters are accepted.
- **Email** – must be in standard `user@domain.tld` format.
- **First Name / Last Name** – must not be blank.

---

## 8. Update User

### How to open

Click **✏ Update User** in the sidebar.

### Steps

**Step 1 – Look up the user**

1. Enter the Oracle Fusion **User ID** in the *User ID* field.
2. Click **Look Up**.
   - The current values for First Name, Last Name, Work Email, and Description are loaded into the edit fields.
   - A status message confirms the user was found.

**Step 2 – Edit and save**

1. Modify any of the editable fields:
   - **First Name**
   - **Last Name**
   - **Work Email**
   - **Description**

   Only fields with a value entered will be sent in the update request. Blank fields are ignored.

2. Click **Save Changes**.
   - On success, a green message confirms the update and lists which fields were changed.

3. Click **Clear** to reset the entire form.

### Notes

- You must look up a user before saving; the User ID field must not be empty when **Save Changes** is clicked.
- If you enter a new email it must pass email format validation.

---

## 9. Lock / Unlock User

### How to open

Click **🔒 Lock / Unlock** in the sidebar.

### Locking an account

1. Enter the Oracle Fusion **User ID**.
2. Click **🔒 Lock Account**.
3. A confirmation dialog appears: *"Lock account for user '…'?"*
   - Click **Yes** to proceed. The account is locked immediately; the user can no longer log in.
   - Click **No** or close the dialog to cancel.

### Unlocking an account

1. Enter the Oracle Fusion **User ID** (same field).
2. Click **🔓 Unlock Account**.
3. Confirm the dialog that appears.
   - On success, the user regains the ability to log in.

> ⚠ **Warning displayed in the panel:** *"Locking an account will immediately prevent the user from logging in."* Both actions are irreversible without performing the opposite action.

---

## 10. Role Management

### How to open

Click **🛡 Role Management** in the sidebar.

### Viewing a user's current roles

1. Enter the Oracle Fusion **Username** (not the User ID).
2. Click **Load Roles**.
   - The scrollable list below shows all roles currently assigned to that user.
   - If no roles exist, "No roles assigned." is displayed.

### Assigning a role

1. Load the target user's roles (see above).
2. In the **Assign role** section, enter the **Role Name** (e.g. `ORA_PER_EMPLOYEE_ABSTRACT`).
3. Click **Assign**.
   - On success, the roles list refreshes automatically to include the new role.

### Removing a role

1. Load the target user's roles.
2. Each role row includes a **Remove** button on the right.
3. Click **Remove** next to the role you want to revoke.
4. Confirm the dialog that appears.
   - On success, the role is removed and the list refreshes.

> ℹ Role names in Oracle Fusion are case-sensitive and follow the format `ORA_<MODULE>_<ROLE>`. Verify the exact name in your Oracle Fusion environment before assigning.

---

## 11. Audit Log

### How to open

Click **📋 Audit Log** in the sidebar.

### Reading the log

The log table shows all actions performed during the current session (and any prior entries appended to `audit_log.csv`), with the most recent entry at the top.

| Column | Description |
|---|---|
| **Timestamp** | Date and time the action was performed |
| **Action** | Type of operation (e.g. `CREATE_USER`, `LOCK_USER`, `ASSIGN_ROLE`) |
| **Target User** | Username or User ID the action was performed on |
| **Result** | `success` (green) or `error` (red) |
| **Message** | Details of the outcome or error |

### Refreshing

Click **⟳ Refresh** to reload the log entries from disk (useful if the file was updated externally).

### Exporting to CSV

1. Click **⬇ Export CSV**.
2. A save-file dialog opens. Choose a location and filename (a timestamp-based default name is pre-filled).
3. Click **Save**. A success message confirms how many entries were exported.

> The log is also persisted automatically to `audit_log.csv` in the application directory throughout the session.

---

## 12. Tips & Troubleshooting

### "Not connected" status

The sidebar shows **⬤ Not connected** until you apply a Base URL in the **Settings** panel. Go to Settings and enter your Oracle Fusion URL, then click **Apply Settings**.

### Connection errors on action

If an API call fails (e.g. 401 Unauthorised, 404 Not Found), the error is displayed in the red status bar below the form and recorded in the Audit Log. Common causes:

| Error | Likely cause | Fix |
|---|---|---|
| 401 Unauthorised | Wrong credentials or expired token | Update credentials in Settings |
| 404 Not Found | User ID or username does not exist | Verify the ID/username in Oracle Fusion |
| 5xx Server Error | Oracle Fusion temporary outage | The app retries automatically; try again after a moment |
| Connection timeout | Network issue or wrong Base URL | Check the URL in Settings |

### Credentials not persisting after restart

Settings entered in the **Settings** panel are session-only. To make them persistent, add them to your `.env` file or `config.json` (see [Section 3](#3-configuration)).

### Role name not recognised

Role names are case-sensitive. Use the exact Oracle Fusion role code (typically uppercase with underscores, e.g. `ORA_FND_APPLICATION_ADMINISTRATOR_JOB`).

### Viewing detailed logs

Set `APP_LOG_LEVEL=DEBUG` in your `.env` file before launching to enable verbose console output. This is useful when diagnosing unexpected API behaviour.

### Running the test suite

```bash
python -m pytest tests/ -v
```

No live Oracle Fusion connection is required; all HTTP calls are mocked.
