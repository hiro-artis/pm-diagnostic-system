# gcloud Authentication via Playwright MCP - Integration Checklist

## Pre-Deployment Checklist

Use this checklist to verify the implementation is complete and ready.

### Configuration Files

- [x] `~/.claude/settings.json` - MCP Playwright enabled globally
  - Check: `cat ~/.claude/settings.json | jq .enabledMcpjsonServers`
  - Expected: `["playwright"]`

- [x] `.claude/settings.json` - Project hook configured
  - Check: `cat .claude/settings.json | jq .hooks`
  - Expected: PostToolUseFailure hook for Bash(gcloud *)

- [x] Both files valid JSON
  - Check: `jq . ~/.claude/settings.json > /dev/null && echo OK`
  - Check: `jq . .claude/settings.json > /dev/null && echo OK`

### Automation Scripts

- [x] `scripts/gcloud-auth-playwright.js` exists
  - Check: `test -f scripts/gcloud-auth-playwright.js && echo OK`
  - Executable: `test -x scripts/gcloud-auth-playwright.js && echo OK`
  - Size: ~450 lines, features Google OAuth automation

- [x] `scripts/gcloud-auth-mcp.sh` exists
  - Check: `test -f scripts/gcloud-auth-mcp.sh && echo OK`
  - Executable: `test -x scripts/gcloud-auth-mcp.sh && echo OK`
  - Size: ~200 lines, orchestration wrapper

### Documentation

- [x] `docs/GCLOUD_AUTH_MCP_SETUP.md` - Comprehensive guide (600+ lines)
- [x] `docs/GCLOUD_AUTH_QUICKSTART.md` - Quick reference (120 lines)
- [x] `docs/PLAYWRIGHT_DEPENDENCIES.md` - Dependency guide (400+ lines)
- [x] `GCLOUD_AUTH_IMPLEMENTATION.md` - Implementation summary
- [x] `GCLOUD_AUTH_CHECKLIST.md` - This checklist

### Permissions

- [x] Global `~/.claude/settings.json` permissions configured
  ```json
  {
    "allow": ["Bash(gcloud *)", "Bash(node *)", "Bash(npm *)", "Bash"]
  }
  ```

- [x] Project `.claude/settings.json` permissions configured
  ```json
  {
    "allow": ["Bash(gcloud *)", "Bash(node scripts/gcloud-auth-*.js)"]
  }
  ```

---

## Pre-Use Setup Checklist

Complete these steps before using the automation.

### 1. Store Google Password
```bash
✓ Run: claude password-manager store GCLOUD_AUTH_PASSWORD
✓ Enter your Google account password
✓ Verify: claude password-manager get GCLOUD_AUTH_PASSWORD
```
**Status:** ___ (Do not proceed without this)

### 2. Install Playwright
```bash
✓ Run: npm install -g @playwright/test
✓ Verify: npm list -g @playwright/test
✓ Check version: npx playwright --version
```
**Status:** ___ (required for browser automation)

### 3. Verify Playwright Installation
```bash
✓ Run: npx playwright install chromium
✓ Check: npx playwright install-deps
✓ Verify cache: ls ~/.cache/ms-playwright/chromium-*/
```
**Status:** ___ (installs browser binaries)

### 4. Test Scripts Directly
```bash
✓ Run: cd /Users/h.tsuchiyama/PM協会テスト診断/PM協会テスト診断
✓ Run: GCLOUD_AUTH_EMAIL=hiro@artis-inc.co.jp \
       GCLOUD_AUTH_PASSWORD="$(claude password-manager get GCLOUD_AUTH_PASSWORD)" \
       ./scripts/gcloud-auth-mcp.sh
✓ Expected output: "AUTHENTICATION_SUCCESSFUL"
```
**Status:** ___ (should complete in 20-40 seconds)

### 5. Verify gcloud Authentication
```bash
✓ Run: gcloud auth list
✓ Check for: hiro@artis-inc.co.jp (marked as active)
✓ Run: gcloud config get-value account
✓ Expected: hiro@artis-inc.co.jp
```
**Status:** ___ (confirms authentication worked)

### 6. Test Hook Integration
```bash
✓ Trigger gcloud command that requires auth
✓ Watch for hook execution in Claude Code
✓ Should see: "Authenticating with gcloud via Playwright..."
✓ After completion, retry the gcloud command
```
**Status:** ___ (validates hook triggering)

---

## Validation Tests

Run these tests to confirm everything is working.

### Test 1: Script Execution
```bash
TEST_RESULT=$(cd /Users/h.tsuchiyama/PM協会テスト診断/PM協会テスト診断 && \
  GCLOUD_AUTH_EMAIL=hiro@artis-inc.co.jp \
  GCLOUD_AUTH_PASSWORD="$(claude password-manager get GCLOUD_AUTH_PASSWORD)" \
  timeout 60 ./scripts/gcloud-auth-mcp.sh 2>&1 | tail -1)

if [[ "$TEST_RESULT" == "AUTHENTICATION_SUCCESSFUL" ]]; then
  echo "PASS: Script execution"
else
  echo "FAIL: Script execution - $TEST_RESULT"
fi
```
**Expected:** PASS

### Test 2: Configuration Syntax
```bash
echo "Checking ~/.claude/settings.json..."
jq -e '.enabledMcpjsonServers[0] == "playwright"' ~/.claude/settings.json > /dev/null && \
  echo "PASS: Playwright MCP enabled" || echo "FAIL: Playwright MCP not configured"

echo "Checking .claude/settings.json..."
jq -e '.hooks.PostToolUseFailure[0].matcher == "Bash"' \
  /Users/h.tsuchiyama/PM協会テスト診断/PM協会テスト診断/.claude/settings.json > /dev/null && \
  echo "PASS: Hook configured" || echo "FAIL: Hook not configured"
```
**Expected:** PASS on both

### Test 3: Permission Rules
```bash
echo "Checking permission rules..."
jq '.permissions.allow[]' ~/.claude/settings.json | grep -q 'Bash(gcloud' && \
  echo "PASS: gcloud permission set" || echo "FAIL: gcloud permission missing"

jq '.permissions.allow[]' ~/.claude/settings.json | grep -q 'Bash(node' && \
  echo "PASS: node permission set" || echo "FAIL: node permission missing"
```
**Expected:** PASS on both

### Test 4: gcloud Integration
```bash
echo "Testing gcloud authentication..."
gcloud auth list 2>&1 | grep -q "hiro@artis-inc.co.jp" && \
  echo "PASS: gcloud authenticated" || echo "FAIL: gcloud not authenticated"

gcloud config get-value account 2>&1 | grep -q "hiro@artis-inc.co.jp" && \
  echo "PASS: Account configured" || echo "FAIL: Account not configured"
```
**Expected:** PASS on both

---

## Troubleshooting Quick Reference

If tests fail, use this table to diagnose.

| Symptom | Diagnosis | Solution |
|---------|-----------|----------|
| "GCLOUD_AUTH_PASSWORD not set" | Password not stored | `claude password-manager store GCLOUD_AUTH_PASSWORD` |
| Script timeout | Playwright not installed | `npm install -g @playwright/test` |
| Browser won't launch | Chromium not found | `npx playwright install chromium` |
| "Failed to extract code" | OAuth flow issue | Enable debug: `GCLOUD_AUTH_HEADLESS=false` |
| Hook not triggering | Config syntax error | Validate: `jq . .claude/settings.json` |
| gcloud auth fails | Still unauthenticated | Run script again: `./scripts/gcloud-auth-mcp.sh` |

**See full troubleshooting:** `docs/GCLOUD_AUTH_MCP_SETUP.md`

---

## Post-Implementation Verification

After setup, verify these critical components.

### Scripts Status
```bash
ls -l scripts/gcloud-auth-*.{js,sh}
# Should show:
# -rwxr-xr-x gcloud-auth-playwright.js
# -rwxr-xr-x gcloud-auth-mcp.sh
```

### Configuration Status
```bash
echo "Global config:" && jq .enabledMcpjsonServers ~/.claude/settings.json
echo "Project config:" && jq '.hooks.PostToolUseFailure[0].command' .claude/settings.json
```

### Documentation Status
```bash
wc -l docs/GCLOUD_AUTH_*.md GCLOUD_AUTH_*.md
# Should show files with substantial content (100+ lines each)
```

### Cache Directory
```bash
mkdir -p ~/.gcloud-auth-cache
ls -la ~/.gcloud-auth-cache/
# Should have write permissions (rwx for user)
```

---

## Sign-Off Checklist

Before considering implementation complete, verify:

- [ ] All configuration files created and valid JSON
- [ ] Both automation scripts executable
- [ ] All documentation files created
- [ ] Google password stored in secure storage
- [ ] Playwright installed and verified
- [ ] Script tested and returns AUTHENTICATION_SUCCESSFUL
- [ ] gcloud authentication verified with `gcloud auth list`
- [ ] Hook configuration validated
- [ ] Cache directory exists with proper permissions
- [ ] All tests in "Validation Tests" section pass

**Implementation Status:** _______________

**Approved By:** _____________________

**Date Completed:** ___________________

---

## Maintenance Schedule

### Weekly
- [ ] Check logs: `tail ~/.gcloud-auth-cache/gcloud-auth.log`
- [ ] Verify auth still works: `gcloud auth list`

### Monthly
- [ ] Update Playwright: `npm update -g @playwright/test`
- [ ] Refresh browsers: `npx playwright install`
- [ ] Check for errors: `grep ERROR ~/.gcloud-auth-cache/gcloud-auth.log`

### Quarterly
- [ ] Review security settings in `.claude/settings.json`
- [ ] Audit hook permissions
- [ ] Update documentation with any learnings

---

## Support Resources

| Resource | Location | Purpose |
|----------|----------|---------|
| Quick Start | `docs/GCLOUD_AUTH_QUICKSTART.md` | Fast setup guide |
| Full Guide | `docs/GCLOUD_AUTH_MCP_SETUP.md` | Comprehensive reference |
| Dependencies | `docs/PLAYWRIGHT_DEPENDENCIES.md` | Dependency troubleshooting |
| Implementation | `GCLOUD_AUTH_IMPLEMENTATION.md` | Technical overview |
| Logs | `~/.gcloud-auth-cache/gcloud-auth.log` | Execution logs |

---

## Emergency Procedures

### If Authentication Loop Occurs
```bash
# Clear recent authentications
gcloud auth revoke

# Manually re-authenticate
gcloud auth login

# Or use the script directly
./scripts/gcloud-auth-mcp.sh
```

### If Hook Keeps Failing
```bash
# Disable hook temporarily
cp .claude/settings.json .claude/settings.json.bak
jq '.hooks.PostToolUseFailure = null' .claude/settings.json.bak > .claude/settings.json

# Diagnose issue
GCLOUD_AUTH_HEADLESS=false ./scripts/gcloud-auth-mcp.sh

# Restore hook after fixing
mv .claude/settings.json.bak .claude/settings.json
```

### If Playwright Corrupted
```bash
# Clean and reinstall
npm uninstall -g @playwright/test
rm -rf ~/.cache/ms-playwright
npm install -g @playwright/test
npx playwright install
```

---

## Rollback Instructions

If you need to revert the implementation:

1. **Revert Configuration:**
   ```bash
   # Remove Playwright from global settings
   jq 'del(.enabledMcpjsonServers)' ~/.claude/settings.json > ~/.claude/settings.json.tmp
   mv ~/.claude/settings.json.tmp ~/.claude/settings.json
   
   # Remove project hook
   rm .claude/settings.json
   ```

2. **Remove Scripts:**
   ```bash
   rm -rf scripts/gcloud-auth-*.{js,sh}
   ```

3. **Remove Documentation:**
   ```bash
   rm -rf docs/GCLOUD_AUTH_*.md GCLOUD_AUTH_*.md
   ```

4. **Clear Cache:**
   ```bash
   rm -rf ~/.gcloud-auth-cache/
   ```

5. **Keep or Clear Password:**
   ```bash
   # If needed in future
   # claude password-manager list
   # claude password-manager delete GCLOUD_AUTH_PASSWORD
   ```

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-06  
**Status:** Ready for Implementation
