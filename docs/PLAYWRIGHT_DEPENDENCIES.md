# Playwright MCP Dependencies

## Installation Guide

### 1. Global Installation (Recommended for Claude Code)

```bash
# Install Playwright globally
npm install -g @playwright/test

# Verify installation
npx playwright --version
```

### 2. Project-Level Installation

If you prefer to install Playwright in the project:

```bash
# Add to package.json
npm install --save-dev @playwright/test

# Or manually add to package.json:
{
  "devDependencies": {
    "@playwright/test": "^1.40.0"
  }
}

npm install
```

### 3. Dockerfile Setup (for Cloud Run)

```dockerfile
FROM node:18-alpine

# Install Playwright dependencies
RUN apk add --no-cache \
    chromium \
    firefox \
    webkit \
    libxrender \
    libxrandr \
    && npm install -g @playwright/test

WORKDIR /app
COPY . .

# Run your application
CMD ["node", "index.js"]
```

---

## Required System Dependencies

### macOS

```bash
# Using Homebrew
brew install chromium

# Or let Playwright install browsers
npx playwright install
```

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    chromium-browser \
    firefox \
    webkit \
    libxss1 \
    libappindicator1 \
    libindicator7

# Or let Playwright install
npx playwright install-deps
```

### Linux (Alpine)

```bash
# Lightweight option for containers
apk add --no-cache \
    chromium \
    firefox-esr \
    webkit
```

---

## Playwright Browsers

By default, Playwright includes three browser engines:

| Browser | Size | Command |
|---------|------|---------|
| Chromium | ~150MB | `chromium.launch()` |
| Firefox | ~100MB | `firefox.launch()` |
| WebKit | ~80MB | `webkit.launch()` |

### Install Specific Browsers Only

```bash
# Install only Chromium (used by gcloud-auth)
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install -g @playwright/test
npx playwright install chromium

# For CI/CD efficiency
PLAYWRIGHT_BROWSERS_PATH=/tmp/pw-browsers npx playwright install chromium
```

---

## Claude Code Integration

### Enable in ~/.claude/settings.json

```json
{
  "enabledMcpjsonServers": ["playwright"],
  "permissions": {
    "allow": [
      "Bash(node *)",
      "Bash(gcloud *)"
    ]
  }
}
```

### Enable in .claude/settings.json (project-level)

```json
{
  "enabledMcpjsonServers": ["playwright"],
  "hooks": {
    "PostToolUseFailure": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash scripts/gcloud-auth-mcp.sh",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

---

## Troubleshooting Installation

### Issue: "Module not found: playwright"

**Solution 1: Check global installation**

```bash
which npx
npm list -g @playwright/test

# If not installed:
npm install -g @playwright/test
```

**Solution 2: Use npx directly**

```bash
npx @playwright/test --version
```

**Solution 3: Install locally in project**

```bash
npm install --save-dev @playwright/test
npx playwright --version
```

### Issue: "Chrome not found"

**Solution:**

```bash
# Install browser binaries
npx playwright install

# Or install specific browser
npx playwright install chromium

# Verify
npx playwright install-deps
```

### Issue: "Cannot find module '@playwright/test' in node_modules"

**Solution:**

```bash
# Clear npm cache
npm cache clean --force

# Reinstall
npm install -g @playwright/test
npm link @playwright/test
```

---

## Environment Variables

### Playwright Configuration

```bash
# Use specific browser binary
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Disable sandbox (for CI/headless environments)
PLAYWRIGHT_DISABLE_SANDBOX=1

# Enable debug logging
DEBUG=pw:api

# Custom browsers path
PLAYWRIGHT_BROWSERS_PATH=/opt/browsers
```

### In gcloud-auth Scripts

```bash
# Optimize for your environment
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export DEBUG=pw:browser

node scripts/gcloud-auth-playwright.js
```

---

## Performance Optimization

### Faster Installs for CI

```bash
# Skip downloading browsers initially
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci

# Download only needed browser before running
npx playwright install chromium --with-deps

# Then run your script
node scripts/gcloud-auth-playwright.js
```

### Reduce Bundle Size

For Docker images, only install Chromium:

```dockerfile
RUN PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install -g @playwright/test && \
    npx playwright install chromium
```

---

## Version Management

### Check Current Version

```bash
npx playwright --version
npm view @playwright/test version
```

### Update to Latest

```bash
npm install -g @playwright/test@latest
npx playwright install
```

### Pin to Specific Version

```bash
npm install -g @playwright/test@1.40.0

# Or in package.json
{
  "devDependencies": {
    "@playwright/test": "^1.40.0"
  }
}
```

---

## Playwright API Reference

### Node.js Script Usage

```javascript
const { chromium } = require('@playwright/test');

async function runBrowser() {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox']
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  await page.goto('https://example.com');
  await page.screenshot({ path: 'example.png' });
  
  await browser.close();
}

runBrowser().catch(err => console.error(err));
```

### gcloud-auth Script Usage

```javascript
const { chromium } = require('playwright');

// Script handles:
// - Browser launch with sandbox options
// - Page navigation and timeouts
// - Form filling and input handling
// - Screenshot/debugging
// - Resource extraction (auth code)
// - Graceful shutdown
```

---

## Documentation Links

- [Playwright Official Docs](https://playwright.dev/)
- [Playwright GitHub](https://github.com/microsoft/playwright)
- [Playwright npm Package](https://www.npmjs.com/package/@playwright/test)
- [Claude Code MCP Integration](https://claude.com/docs/mcp)

---

## Support

### Check Installation Health

```bash
# Comprehensive check
npx playwright doctor

# Specific browser check
npx playwright install-deps chromium
npx playwright install chromium

# Run test
npx playwright test --list
```

### Debug Commands

```bash
# Enable verbose logging
DEBUG=pw:* node scripts/gcloud-auth-playwright.js

# Run Playwright inspector
npx playwright codegen https://google.com

# Check version compatibility
npm view @playwright/test@latest peerDependencies
```

---

**Last Updated:** 2026-06-06  
**Playwright Version:** 1.40.0+  
**Status:** Production Ready
