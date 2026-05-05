# Getting Started

This guide is divided into two parts:

1. [**Permissions — concepts, roles, and access scope**](#permissions--concepts-roles-and-access-scope) — what the available permissions are, who is responsible for each, and what content they grant access to.
2. [**Step-by-step setup for `Sites.Selected`**](#step-by-step-setup-for-sitesselected) — the concrete actions each role must perform to configure and run the project.

---

## Permissions: concepts, roles, and access scope

### Roles involved

Three distinct roles participate in setting up application access to SharePoint
via the Microsoft Graph API.  Steps in Part 2 are tagged with the badge of the
role responsible.

| Badge | Role | Description |
|---|---|---|
| 🔧 **Dev team** | Application developer | Creates the app registration and writes the code. |
| 🔑 **Entra Admin** | Azure AD / Entra ID administrator | Holds the **Application Administrator** (or Global Administrator) role. Grants admin consent for API permissions in the Azure portal. |
| 🛡️ **SP Admin** | SharePoint tenant administrator | Holds the **SharePoint Administrator** role in the Microsoft 365 Admin Center. **This is not the same as a site collection administrator (site owner).** A site owner manages users within a site but cannot grant Graph API application access — that requires tenant-level SharePoint admin rights. |

### Available Graph API permissions for SharePoint

The Microsoft Graph API offers two tiers of application permissions for
SharePoint access:

| Permission | Scope | Notes |
|---|---|---|
| `Sites.Read.All` | All sites in the tenant | Read-only, no restriction by site |
| `Sites.ReadWrite.All` | All sites in the tenant | Read and write, no restriction by site |
| `Sites.Selected` | Only explicitly enrolled sites | Least-privilege; recommended for all non-trivial deployments |

Tenant-wide permissions (`Sites.Read.All`, `Sites.ReadWrite.All`) are simple to
configure but grant the application access to every SharePoint site in the
organisation.  A compromised credential would expose all content tenant-wide.
They are **not used in this project** and are only mentioned here for
completeness.

**`Sites.Selected` is the approach used throughout this guide.**

### What `Sites.Selected` grants access to

`Sites.Selected` by itself grants the application access to nothing.  The
SharePoint tenant administrator must separately enrol each site the app is
allowed to access, choosing either `read` or `write` level.

Once a site is enrolled, the grant covers **all content within that site
collection**:

| Content type | Read grant | Write grant |
|---|:---:|:---:|
| Document libraries — enumerate folders and files | ✅ | ✅ |
| Document libraries — download file content | ✅ | ✅ |
| Document libraries — upload or overwrite files | ❌ | ✅ |
| File metadata (name, size, timestamps, URL) | ✅ | ✅ |
| Lists — read items and field values | ✅ | ✅ |
| Lists — create or update items | ❌ | ✅ |

> **Granularity limit:** `Sites.Selected` is the finest-grained application
> permission available in the Microsoft Graph API.  It is not possible to
> restrict access to a single document library or list *within* a site via
> Graph permissions alone.  If sub-site isolation is required, enforce it in
> the application layer by validating the drive ID or list ID before acting.

The `read` and `write` roles in `Sites.Selected` map to the same underlying
access level as `Sites.Read.All` and `Sites.ReadWrite.All` — the only
difference is scope: access is restricted to explicitly enrolled sites.

Grant `read` when the application only needs to read.  Grant `write` only to
sites that require it.  Use separate app registrations if different sites need
different access levels.

### Authentication flow: client credentials vs. delegated (user) authentication

This project uses the **client credentials** OAuth 2.0 flow, where the app
authenticates as itself (the app registration) with no user context:

- ✅ **Unattended execution** — no user sign-in required; suitable for batch jobs, background services, or scheduled tasks.
- ✅ **Simple setup** — a single client ID and secret.
- ❌ **Audit trail** — SharePoint activity logs record actions by the app identity, not the user running the code.

**Alternative: delegated authentication** — if you need to track actions by the
user running the app, you can switch to the **authorization code flow**, where
a user signs in interactively:

- ✅ **User audit trail** — SharePoint logs identify the specific user who
  performed each action.
- ❌ **Requires user interaction** — the app cannot run unattended; someone must
  sign in each time.

Both flows use the same `Sites.Selected` permission model and grant the same
access to SharePoint content. The difference is **who the app represents**
(itself vs. a user) and how that identity appears in audit logs.

Switching to delegated auth requires:

1. Changing the token acquisition in `src/msgraphtest/auth.py` from the client
   credentials endpoint to the authorization code flow (using a library like
   [MSAL for Python](https://github.com/AzureAD/microsoft-authentication-library-for-python) 
   with `acquire_token_interactive()`).
2. Adding a **Redirect URI** in the app registration (e.g.
   `http://localhost:8000`) to handle the OAuth callback.
3. User(s) signing in when the app runs.

For most scenarios, **client credentials (current approach) is simpler**. Use
delegated auth only if your governance or compliance requirements mandate an
audit trail linking each SharePoint action to a named user.

## Step-by-step setup for `Sites.Selected`

### Who does what — overview

| Step | Action | 🔧 Dev | 🔑 Entra Admin | 🛡️ SP Admin |
|---|---|:---:|:---:|:---:|
| 1 | Create app registration and client secret | ✅ | | |
| 2 | Add `Sites.Selected` permission | ✅ | | |
| 2 | Grant admin consent | | ✅ | |
| 3 | Discover the SharePoint site ID | ✅ | | |
| 4 | Enrol the site for the app | | | ✅ |
| 5 | Discover drive ID and list ID | ✅ | | |
| 6 | Configure `.env` and run | ✅ | | |

---

### Step 1 — Create the app registration and client secret

> 🔧 **Dev team**

1. Open the [Azure portal](https://portal.azure.com) → **Microsoft Entra ID** → **App registrations** → **New registration**.
2. **Name**: choose a descriptive name, e.g. `MSGraphTest-SharePoint`.
3. **Supported account types**: select **Accounts in this organizational directory only**.
4. Leave **Redirect URI** blank (client credentials flow — no user sign-in).
5. Click **Register** and note:
   - **Application (client) ID** → `AZURE_CLIENT_ID`
   - **Directory (tenant) ID** → `AZURE_TENANT_ID`
6. Go to **Certificates & secrets** → **Client secrets** → **New client secret**.
7. Set a description and an expiry aligned with your rotation policy (max 24 months).
8. Click **Add** and **immediately copy** the secret value → `AZURE_CLIENT_SECRET`.

> ⚠️ The secret value is shown only once. Store it securely (e.g. Azure Key Vault). If you navigate away without copying it, delete and recreate it.

---

### Step 2 — Add `Sites.Selected` and grant admin consent

> 🔧 **Dev team** adds the permission.  🔑 **Entra Admin** grants consent.

1. In the app registration go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Application permissions**.
2. Search for and add **`Sites.Selected`** only.
3. Click **Grant admin consent for \<tenant\>** (requires Entra Admin) and confirm.

> `Sites.Selected` grants no site access yet — that happens in Step 4.

---

### Step 3 — Discover the SharePoint site ID

> 🔧 **Dev team**

This step uses a **short-lived delegated token** (your personal user account)
solely to look up the site ID string.  This token is independent of the app's
credentials: it grants nothing to the app registration, leaves no lasting
state, and is not used anywhere after this step.  The application itself always
authenticates with a separate client-credential token (app identity) acquired
in Step 5.

Obtain the delegated token using the Azure CLI:

```bash
az login
TOKEN=$(az account get-access-token --resource https://graph.microsoft.com --query accessToken -o tsv)
```

Query the site:

```bash
# Replace <hostname> and <site-path> with your values
# Example: contoso.sharepoint.com and sites/ProjectAlpha
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://graph.microsoft.com/v1.0/sites/<hostname>:/sites/<site-path>" \
  | python -m json.tool
```

Copy the `id` field from the response → `SHAREPOINT_SITE_ID`.  
Format: `contoso.sharepoint.com,xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx,yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy`

Share this value with the SP Admin before proceeding to Step 4.

---

### Step 4 — Enrol the site for the app

> 🛡️ **SP Admin** (SharePoint tenant administrator)

> ⚠️ The account performing this step must hold the **SharePoint Administrator**
> or **Global Administrator** role in Microsoft 365.  A site collection
> administrator / site owner cannot call `POST /sites/{site-id}/permissions`.

Obtain an admin token:

```bash
az login  # sign in with the SP Admin account
TOKEN=$(az account get-access-token --resource https://graph.microsoft.com --query accessToken -o tsv)
SITE_ID="<SHAREPOINT_SITE_ID from Step 3>"
APP_ID="<AZURE_CLIENT_ID from Step 1>"
```

**Grant read-only access:**

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://graph.microsoft.com/v1.0/sites/${SITE_ID}/permissions" \
  -d '{
    "roles": ["read"],
    "grantedToIdentities": [{
      "application": {
        "id": "'"${APP_ID}"'",
        "displayName": "MSGraphTest-SharePoint"
      }
    }]
  }'
```

**Grant read + write access** (replace `"read"` with `"write"` — write implicitly includes read):

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://graph.microsoft.com/v1.0/sites/${SITE_ID}/permissions" \
  -d '{
    "roles": ["write"],
    "grantedToIdentities": [{
      "application": {
        "id": "'"${APP_ID}"'",
        "displayName": "MSGraphTest-SharePoint"
      }
    }]
  }'
```

**Verify the grant:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://graph.microsoft.com/v1.0/sites/${SITE_ID}/permissions" \
  | python -m json.tool
```

**Revoke a grant** (if needed — use the `id` returned by the verify call above):

```bash
curl -s -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  "https://graph.microsoft.com/v1.0/sites/${SITE_ID}/permissions/<permission-id>"
```

---

### Step 5 — Discover the drive ID and list ID

> 🔧 **Dev team** — uses the app's own client-credential token.

```bash
TOKEN=$(curl -s -X POST \
  "https://login.microsoftonline.com/${AZURE_TENANT_ID}/oauth2/v2.0/token" \
  -d "grant_type=client_credentials" \
  -d "client_id=${AZURE_CLIENT_ID}" \
  -d "client_secret=${AZURE_CLIENT_SECRET}" \
  -d "scope=https://graph.microsoft.com/.default" \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

**Find the drive ID:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://graph.microsoft.com/v1.0/sites/${SHAREPOINT_SITE_ID}/drives" \
  | python -m json.tool
```

Pick the entry whose `name` matches your document library and copy its `id` → `SHAREPOINT_DRIVE_ID`.

**Find the list ID:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://graph.microsoft.com/v1.0/sites/${SHAREPOINT_SITE_ID}/lists" \
  | python -m json.tool
```

Pick the list you want to work with and copy its `id` → `SHAREPOINT_LIST_ID`.

---

### Step 6 — Configure `.env` and run

> 🔧 **Dev team**

```bash
uv sync
cp .env.example .env
```

Edit `.env` with all values collected above:

```ini
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=<your-secret-value>
SHAREPOINT_SITE_ID=contoso.sharepoint.com,<site-guid>,<web-guid>
SHAREPOINT_DRIVE_ID=b!<drive-id>
SHAREPOINT_LIST_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Verify connectivity:

```bash
uv run examples/example_drive_list.py
uv run examples/example_list_get.py
```
