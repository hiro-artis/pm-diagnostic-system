# gcloud Authentication via Playwright - Quick Start

## 30-Second Setup

### Step 1: Store Password
```bash
claude password-manager store GCLOUD_AUTH_PASSWORD
# Enter your Google account password when prompted
```

### Step 2: Install Playwright
```bash
npm install -g @playwright/test
```

### Step 3: Test Authentication
```bash
cd /Users/h.tsuchiyama/PM協会テスト診断/PM協会テスト診断
GCLOUD_AUTH_EMAIL=hiro@artis-inc.co.jp \
GCLOUD_AUTH_PASSWORD="$(claude password-manager get GCLOUD_AUTH_PASSWORD)" \
./scripts/gcloud-auth-mcp.sh
```

### Step 4: Verify gcloud is Authenticated
```bash
gcloud auth list
gcloud config get-value account
```

**Done!** Next gcloud command that fails will auto-authenticate.

---

## Common Tasks

### Manual Re-authenticate
```bash
./scripts/gcloud-auth-mcp.sh
```

### See Browser During Auth (Debug)
```bash
GCLOUD_AUTH_HEADLESS=false ./scripts/gcloud-auth-mcp.sh
```

### Check Auth Logs
```bash
tail -50 ~/.gcloud-auth-cache/gcloud-auth.log
```

### Get Last Auth Code
```bash
cat ~/.gcloud-auth-cache/auth-code.txt
```

### Test with Different Email
```bash
GCLOUD_AUTH_EMAIL=other.email@gmail.com \
GCLOUD_AUTH_PASSWORD="..." \
./scripts/gcloud-auth-mcp.sh
```

---

## How It Works

1. **Claude Code Hook** detects gcloud command failure
2. **Hook triggers** `scripts/gcloud-auth-mcp.sh`
3. **Shell script** launches Playwright Node.js script
4. **Playwright** opens headless Chromium browser
5. **Browser automation** logs into Google account
6. **Authorization code** extracted from OAuth flow
7. **Code applied** to gcloud CLI automatically
8. **Next gcloud command** uses new authentication

---

## Files Overview

| File | Purpose | Edit? |
|------|---------|-------|
| `scripts/gcloud-auth-playwright.js` | Playwright automation | No, core logic |
| `scripts/gcloud-auth-mcp.sh` | Orchestration wrapper | No, uses scripts above |
| `.claude/settings.json` | Hook configuration | Yes, customize if needed |
| `docs/GCLOUD_AUTH_MCP_SETUP.md` | Full reference | Read for details |
| `docs/PLAYWRIGHT_DEPENDENCIES.md` | Dependency guide | Read for troubleshooting |

---

## Troubleshooting Quick Links

| Error | Solution |
|-------|----------|
| "GCLOUD_AUTH_PASSWORD not set" | Run: `claude password-manager store GCLOUD_AUTH_PASSWORD` |
| "Playwright not found" | Run: `npm install -g @playwright/test` |
| "Chrome not found" | Run: `npx playwright install chromium` |
| "Timeout waiting for code" | Enable debug: `GCLOUD_AUTH_HEADLESS=false ./scripts/gcloud-auth-mcp.sh` |
| "Failed to extract code" | Check logs: `cat ~/.gcloud-auth-cache/gcloud-auth.log` |

---

## What's Configured

### Global Settings (`~/.claude/settings.json`)
```json
{
  "enabledMcpjsonServers": ["playwright"],
  "permissions": {
    "allow": ["Bash(gcloud *)", "Bash(node *)"]
  }
}
```

### Project Settings (`.claude/settings.json`)
```json
{
  "hooks": {
    "PostToolUseFailure": [
      {
        "matcher": "Bash",
        "if": "Bash(gcloud *)",
        "command": "bash scripts/gcloud-auth-mcp.sh",
        "timeout": 120
      }
    ]
  }
}
```

---

## Next Steps

1. ✓ Password stored → `claude password-manager store GCLOUD_AUTH_PASSWORD`
2. ✓ Playwright installed → `npm install -g @playwright/test`
3. ✓ Test script → `./scripts/gcloud-auth-mcp.sh`
4. ✓ Hook configured → `.claude/settings.json` (already set)
5. Try running a gcloud command → watch hook trigger on failure

---

## Security Reminders

- Never commit passwords to git
- Password stored in Claude Code secure storage (encrypted)
- Auth codes are single-use, short-lived tokens
- Browser runs sandboxed, no persistent cookies
- .gitignore contains `~/.gcloud-auth-cache/` to prevent accidental leaks

---

## Need Help?

1. **Check logs:** `tail ~/.gcloud-auth-cache/gcloud-auth.log`
2. **See browser:** `GCLOUD_AUTH_HEADLESS=false ./scripts/gcloud-auth-mcp.sh`
3. **Run tests:** `node scripts/gcloud-auth-playwright.js 2>&1 | tail -50`
4. **Read full guide:** `docs/GCLOUD_AUTH_MCP_SETUP.md`
5. **Verify setup:** `gcloud auth list`

---

**Status:** Ready to use  
**Last Updated:** 2026-06-06  
**Tested On:** macOS, Chrome/Chromium
