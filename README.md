# MSGraphTest — SharePoint via Microsoft Graph API

A Python test project demonstrating how to access SharePoint through the
**Microsoft Graph API** using MSAL for authentication.  Operations covered
include document library (drive) management and SharePoint list manipulation.

Licensed under the [GNU General Public License v3.0](LICENSE).

---

## Project structure

```
MSGraphTest/
├── src/
│   └── msgraphtest/
│       ├── __init__.py        # package entry-point
│       ├── auth.py            # MSAL client-credentials token helper
│       ├── graph_client.py    # thin HTTP wrapper for Graph REST calls
│       ├── drive.py           # document library operations
│       └── lists.py           # SharePoint list operations
├── tests/
│   ├── test_auth.py
│   ├── test_drive.py
│   └── test_lists.py
├── examples/
│   ├── example_drive_list.py       # list drive root contents
│   ├── example_drive_download.py   # download a file to local folder
│   ├── example_drive_upload.py     # upload a local file
│   ├── example_drive_read_write.py # read & update file text content
│   ├── example_list_get.py         # retrieve all list items
│   ├── example_list_create.py      # create a list item
│   └── example_list_update.py      # update a list item
├── docs/
│   └── getting_started.md
├── downloads/                 # (git-ignored) local download target
├── .env.example               # copy to .env and fill in credentials
├── pyproject.toml
└── LICENSE
```

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python ≥ 3.11 | Tested with 3.11+ |
| [UV](https://docs.astral.sh/uv/) | Package & virtual-env manager |
| Azure AD App Registration | With `Sites.Read.All` / `Sites.ReadWrite.All` MS Graph permissions |

---

## Quick start

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd MSGraphTest
uv sync
```

### 2. Configure credentials

```bash
cp .env.example .env
# edit .env with your Azure AD and SharePoint details
```

Required variables in `.env`:

| Variable | Description |
|---|---|
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_CLIENT_ID` | App registration client ID |
| `AZURE_CLIENT_SECRET` | App registration client secret |
| `SHAREPOINT_SITE_ID` | Graph site ID (e.g. `contoso.sharepoint.com,guid,guid`) |
| `SHAREPOINT_DRIVE_ID` | Drive ID of the document library |
| `SHAREPOINT_LIST_ID` | List ID for list operations |

> **Finding IDs** — see [docs/getting_started.md](docs/getting_started.md).

### 3. Run an example

```bash
uv run examples/example_drive_list.py
uv run examples/example_list_get.py
```

---

## Running tests

```bash
uv run pytest
```

Coverage report is printed automatically.  Tests use mocking and do **not**
require live credentials.

---

## Module overview

### `auth.py`
Acquires a Graph API bearer token using the OAuth 2.0 **client credentials**
flow via [MSAL](https://github.com/AzureAD/microsoft-authentication-library-for-python).

### `graph_client.py`
`GraphClient` — a thin `requests.Session` wrapper that injects the bearer
token and exposes `get`, `post`, `patch`, `put_bytes`, and `get_raw` helpers.

### `drive.py`
Document library operations:

| Function | Description |
|---|---|
| `list_drive_items(folder_path)` | List children of a folder |
| `download_file(item_id, local_path)` | Download a file to disk |
| `upload_file(local_path, remote_folder)` | Upload a local file (≤ 4 MB) |
| `read_file_content(item_id)` | Return file text as a string |
| `write_file_content(item_id, content)` | Overwrite a file's text content |

### `lists.py`
SharePoint list operations:

| Function | Description |
|---|---|
| `get_list_items(select)` | Retrieve all items (optionally select fields) |
| `create_list_item(fields)` | Create a new item |
| `update_list_item(item_id, fields)` | Update fields on an existing item |

---

## License

This project is licensed under the **GNU General Public License v3.0**.
See [LICENSE](LICENSE) for the full text.
