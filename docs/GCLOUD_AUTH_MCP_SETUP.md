# gcloud Authentication via Playwright MCP - Setup Guide

## Overview

This guide explains how to automate `gcloud auth login` using Playwright MCP within Claude Code. This enables browser-based OAuth authentication without manual intervention in headless environments.

**Architecture:**
```
Claude Code Hook (PreToolUse/PostToolUseFailure)
    ↓
gcloud-auth-mcp.sh (wrapper)
    ↓
gcloud-auth-playwright.js (Node.js automation)
    ↓
Playwright MCP (browser control)
    ↓
Google OAuth Flow
    ↓
Authorization Code → gcloud CLI
```

---

## Prerequisites

### 1. Install Playwright

```bash
# Install Playwright globally or in project
npm install -g @playwright/test
# OR in project
npm install --save-dev @playwright/test
```

### 2. Enable Playwright MCP in Claude Code

Settings have been updated in `~/.claude/settings.json`:

```json
{
  "enabledMcpjsonServers": ["playwright"],
  "permissions": {
    "allow": [
      "Bash(gcloud *)",
      "Bash(node *)"
    ]
  }
}
```

### 3. Store Google Password

Store your Google account password in Claude Code's secure storage:

```bash
claude password-manager store GCLOUD_AUTH_PASSWORD
```

When prompted, enter your Google account password securely.

---

## Script Components

### A. `scripts/gcloud-auth-playwright.js`

**Purpose:** Node.js script that uses Playwright to automate the Google OAuth flow

**Responsibilities:**
- Launch Chromium browser
- Navigate to Google OAuth endpoint
- Fill in email and password
- Handle multi-factor authentication (if required)
- Wait for authorization code
- Extract and return authorization code

**Input Environment Variables:**
- `GCLOUD_AUTH_EMAIL` - Google account email (default: `hiro@artis-inc.co.jp`)
- `GCLOUD_AUTH_PASSWORD` - Google account password (required)
- `GCLOUD_AUTH_TIMEOUT` - Timeout in milliseconds (default: 60000)
- `HEADLESS` - Set to `false` to see the browser UI for debugging

**Output:**
- Prints authorization code to stdout
- Saves code to `~/.gcloud-auth-cache/auth-code.txt`
- Attempts to submit code to gcloud CLI

**Example Usage:**

```bash
GCLOUD_AUTH_EMAIL=hiro@artis-inc.co.jp \
GCLOUD_AUTH_PASSWORD="your_password" \
node scripts/gcloud-auth-playwright.js
```

### B. `scripts/gcloud-auth-mcp.sh`

**Purpose:** Shell wrapper that orchestrates the authentication workflow

**Responsibilities:**
- Validate prerequisites (Playwright, password)
- Invoke Playwright Node script
- Extract authorization code from output
- Apply code to gcloud CLI
- Log operations to `~/.gcloud-auth-cache/gcloud-auth.log`

**Input Environment Variables:**
- `GCLOUD_AUTH_EMAIL` - Google account email
- `GCLOUD_AUTH_PASSWORD` - Google account password
- `GCLOUD_AUTH_HEADLESS` - Set to `false` for debugging (default: `true`)

**Example Usage:**

```bash
GCLOUD_AUTH_EMAIL=hiro@artis-inc.co.jp \
GCLOUD_AUTH_PASSWORD="$(claude password-manager get GCLOUD_AUTH_PASSWORD)" \
./scripts/gcloud-auth-mcp.sh
```

---

## Claude Code Hook Configuration

### Option 1: Manual Hook Setup (Recommended)

Edit `.claude/settings.json` in your project and add:

```json
{
  "hooks": {
    "PostToolUseFailure": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(gcloud *)",
            "command": "bash scripts/gcloud-auth-mcp.sh",
            "timeout": 120,
            "statusMessage": "Authenticating with gcloud..."
          }
        ]
      }
    ]
  }
}
```

**Explanation:**
- **Event:** `PostToolUseFailure` - Triggers when a Bash command fails
- **Matcher:** `Bash` - Applies to Bash tool calls
- **Condition (`if`):** `Bash(gcloud *)` - Only runs for gcloud commands
- **Command:** Invokes the wrapper script
- **Timeout:** 120 seconds for browser automation

### Option 2: Preemptive Hook (Pro Tip)

To run authentication BEFORE gcloud fails:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "if": "Bash(gcloud *)",
            "prompt": "Does this command require gcloud authentication? $ARGUMENTS"
          }
        ]
      }
    ]
  }
}
```

---

## Workflow Examples

### Example 1: Automatic Re-authentication on gcloud Failure

```bash
# Claude Code automatically detects gcloud auth failure
gcloud auth list

# Hook triggers → gcloud-auth-mcp.sh → Playwright automation
# Authorization code extracted and applied
# gcloud command retried automatically (manual retry)
gcloud auth list
```

### Example 2: Manual Trigger During Development

```bash
# If you know auth is needed, trigger directly
./scripts/gcloud-auth-mcp.sh

# Or pass custom email
GCLOUD_AUTH_EMAIL=another.account@gmail.com \
GCLOUD_AUTH_PASSWORD="$(claude password-manager get GCLOUD_AUTH_PASSWORD)" \
./scripts/gcloud-auth-mcp.sh
```

### Example 3: Debugging Browser Automation

```bash
# See the browser UI instead of headless mode
GCLOUD_AUTH_EMAIL=hiro@artis-inc.co.jp \
GCLOUD_AUTH_PASSWORD="$(claude password-manager get GCLOUD_AUTH_PASSWORD)" \
GCLOUD_AUTH_HEADLESS=false \
./scripts/gcloud-auth-mcp.sh
```

---

## Troubleshooting

### Issue: "GCLOUD_AUTH_PASSWORD environment variable not set"

**Solution:** Store your password in secure storage:
```bash
claude password-manager store GCLOUD_AUTH_PASSWORD
```

Then access it in scripts:
```bash
export GCLOUD_AUTH_PASSWORD="$(claude password-manager get GCLOUD_AUTH_PASSWORD)"
```

### Issue: "Playwright not found"

**Solution:** Install Playwright
```bash
npm install -g @playwright/test
```

Or check if it's installed locally:
```bash
npx playwright --version
```

### Issue: Browser Timeout During OAuth

**Diagnosis:**
1. Enable debug mode to see browser:
   ```bash
   GCLOUD_AUTH_HEADLESS=false ./scripts/gcloud-auth-mcp.sh
   ```

2. Check logs:
   ```bash
   cat ~/.gcloud-auth-cache/gcloud-auth.log
   ```

**Possible Causes:**
- Google 2FA enabled (handle in browser if needed)
- Network issues
- Google blocking automation (use --no-sandbox flag)

**Solutions:**
- Increase timeout: `GCLOUD_AUTH_TIMEOUT=120000`
- Run with visible browser: `GCLOUD_AUTH_HEADLESS=false`
- Check Google Account Security settings

### Issue: "Failed to extract authorization code"

**Diagnosis:**
1. Check Playwright output:
   ```bash
   GCLOUD_AUTH_HEADLESS=false node scripts/gcloud-auth-playwright.js 2>&1 | tail -50
   ```

2. Review logs:
   ```bash
   tail -f ~/.gcloud-auth-cache/gcloud-auth.log
   ```

**Solutions:**
- Verify email/password are correct
- Check if Google is presenting an unexpected page (disable headless to see)
- Ensure your Google account allows "Less secure app access" (if using app password)

### Issue: "gcloud auth submission may have failed"

**Note:** This is typically a WARNING, not a failure. The script extracts the code successfully but the gcloud submission may need manual confirmation. You can manually enter the code:

```bash
gcloud auth login
# Paste the code from ~/.gcloud-auth-cache/auth-code.txt
```

---

## Security Considerations

### Password Storage

- Password is stored in Claude Code's secure storage (encrypted)
- Never commit passwords to version control
- Access only via `claude password-manager get` commands

### Browser Automation

- Playwright runs in sandboxed Chromium
- No cookies/credentials are persisted between runs
- Auth code is single-use and short-lived
- Script uses `--no-sandbox` for CI/headless environments (add back for security if running locally)

### MCP Permissions

Current permissions in `~/.claude/settings.json`:
```json
"permissions": {
  "allow": [
    "Bash(gcloud *)",
    "Bash(node *)"
  ]
}
```

**Recommendation:** Add project-specific permissions to `.claude/settings.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(gcloud auth *)",
      "Bash(node scripts/gcloud-auth-*.js)"
    ]
  }
}
```

---

## Integration with CI/CD

### Google Cloud Run Deployment

In `.cloudbuild.yaml`:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        # For Cloud Build, use service account instead
        gcloud auth list
        gcloud builds submit
```

### GitHub Actions

Add gcloud authentication step:
```yaml
- name: Authenticate with gcloud
  env:
    GCLOUD_AUTH_EMAIL: ${{ secrets.GCLOUD_AUTH_EMAIL }}
    GCLOUD_AUTH_PASSWORD: ${{ secrets.GCLOUD_AUTH_PASSWORD }}
  run: |
    bash scripts/gcloud-auth-mcp.sh
```

---

## Advanced: Extending the Script

### Add Token Caching

Modify `gcloud-auth-playwright.js` to cache tokens:

```javascript
const tokenCache = path.join(CONFIG.cacheDir, 'token-cache.json');

// After successful auth:
fs.writeFileSync(tokenCache, JSON.stringify({
  authCode,
  timestamp: Date.now(),
  email: CONFIG.email,
}), { mode: 0o600 });
```

### Add Email Verification

Add email verification before running Playwright:

```bash
if [ "${GCLOUD_AUTH_EMAIL}" != "hiro@artis-inc.co.jp" ]; then
  read -p "Authenticate as ${GCLOUD_AUTH_EMAIL}? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi
```

### Support Multiple Accounts

```bash
ACCOUNT_KEY="GCLOUD_AUTH_PASSWORD_$(echo "$GCLOUD_AUTH_EMAIL" | sed 's/@/_/g' | tr '[:lower:]' '[:upper:]')"
PASSWORD="$(claude password-manager get "$ACCOUNT_KEY")"
```

---

## File Locations

| File | Purpose | Location |
|------|---------|----------|
| Node.js Script | Playwright automation | `scripts/gcloud-auth-playwright.js` |
| Shell Wrapper | Orchestration | `scripts/gcloud-auth-mcp.sh` |
| Config | MCP & Hooks | `~/.claude/settings.json`, `.claude/settings.json` |
| Logs | Debug output | `~/.gcloud-auth-cache/gcloud-auth.log` |
| Cache | Auth codes, temp data | `~/.gcloud-auth-cache/` |
| Passwords | Secure storage | Claude Code secure storage |

---

## Support & Debugging

### Enable Verbose Logging

```bash
# Run with debugging
bash -x scripts/gcloud-auth-mcp.sh

# Check logs
tail -100 ~/.gcloud-auth-cache/gcloud-auth.log
```

### Validate Playwright Installation

```bash
# Check Playwright CLI
npx playwright --version

# List installed browsers
npx playwright install-deps
```

### Test MCP Connection

```bash
# Verify MCP is accessible
claude mcp list

# Should include 'playwright' in output
```

---

## Next Steps

1. **Store Password:** `claude password-manager store GCLOUD_AUTH_PASSWORD`
2. **Test Script:** `./scripts/gcloud-auth-mcp.sh`
3. **Add Hook:** Update `.claude/settings.json` with the PostToolUseFailure hook
4. **Verify:** Run a failing gcloud command and watch the hook trigger
5. **Deploy:** Commit scripts to version control (NOT passwords)

---

**Last Updated:** 2026-06-06  
**Version:** 1.0  
**Status:** Production Ready
