#!/usr/bin/env node

/**
 * gcloud-auth-playwright.js
 *
 * Automates Google Cloud authentication via Playwright
 * Handles browser-based OAuth flow for gcloud CLI
 *
 * Usage:
 *   node scripts/gcloud-auth-playwright.js [email] [password]
 *
 * Environment Variables:
 *   GCLOUD_AUTH_EMAIL - Google account email (defaults to hiro@artis-inc.co.jp)
 *   GCLOUD_AUTH_PASSWORD - Google account password (from secure storage)
 *   GCLOUD_AUTH_TIMEOUT - Timeout in ms for auth flow (default: 60000)
 *   HEADLESS - Set to 'false' to see the browser (default: 'true')
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  email: process.env.GCLOUD_AUTH_EMAIL || 'hiro@artis-inc.co.jp',
  password: process.env.GCLOUD_AUTH_PASSWORD || '',
  timeout: parseInt(process.env.GCLOUD_AUTH_TIMEOUT || '60000'),
  headless: process.env.HEADLESS !== 'false',
  cacheDir: path.join(process.env.HOME || '/tmp', '.gcloud-auth-cache'),
};

// Ensure cache directory exists
if (!fs.existsSync(CONFIG.cacheDir)) {
  fs.mkdirSync(CONFIG.cacheDir, { recursive: true });
}

/**
 * Main authentication flow
 */
async function authenticateGCloud() {
  let browser = null;
  let authCode = null;

  try {
    console.error('[gcloud-auth] Starting browser automation for gcloud authentication...');
    console.error(`[gcloud-auth] Using email: ${CONFIG.email}`);
    console.error(`[gcloud-auth] Headless mode: ${CONFIG.headless}`);

    // Launch browser
    browser = await chromium.launch({
      headless: CONFIG.headless,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
      ],
    });

    const context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      ignoreHTTPSErrors: true,
    });

    const page = await context.newPage();

    // Set navigation timeout
    page.setDefaultTimeout(CONFIG.timeout);
    page.setDefaultNavigationTimeout(CONFIG.timeout);

    // Listen for popup windows (auth redirects)
    page.on('popup', async (popup) => {
      console.error('[gcloud-auth] Popup detected, handling...');
      try {
        await popup.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
      } catch (err) {
        console.error('[gcloud-auth] Popup load timeout (expected)', err.message);
      }
    });

    // Navigate to gcloud auth URL
    console.error('[gcloud-auth] Navigating to gcloud OAuth endpoint...');
    const gcloudAuthUrl = 'https://accounts.google.com/o/oauth2/auth?client_id=32555940559.apps.googleusercontent.com&scope=openid%20email%20profile&response_type=code&redirect_uri=urn:ietf:wg:oauth:2.0:oob&access_type=offline';

    try {
      await page.goto(gcloudAuthUrl, { waitUntil: 'networkidle' });
    } catch (err) {
      console.error('[gcloud-auth] Navigation timeout (expected for some pages)', err.message);
    }

    // Wait for email input
    console.error('[gcloud-auth] Waiting for email input field...');
    await page.waitForSelector('input[type="email"]', { timeout: 10000 }).catch(
      () => page.waitForSelector('input#identifierId', { timeout: 5000 })
    );

    // Enter email
    console.error('[gcloud-auth] Entering email address...');
    const emailInputs = await page.$$('input[type="email"], input#identifierId');
    if (emailInputs.length > 0) {
      await emailInputs[0].fill(CONFIG.email);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(2000);
    }

    // Handle password input
    console.error('[gcloud-auth] Waiting for password input...');
    try {
      await page.waitForSelector('input[type="password"]', { timeout: 10000 });
      console.error('[gcloud-auth] Entering password...');
      await page.fill('input[type="password"]', CONFIG.password);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(2000);
    } catch (err) {
      console.error('[gcloud-auth] Password input timeout - may have been auto-filled or 2FA required');
    }

    // Handle potential 2FA/verification prompts
    console.error('[gcloud-auth] Checking for verification prompts...');
    try {
      // Wait for either the auth code page or approval button
      const authCodeElement = await Promise.race([
        page.waitForSelector('div[aria-label*="code"]', { timeout: 5000 }),
        page.waitForSelector('button:has-text("Allow")', { timeout: 5000 }),
        page.waitForSelector('button:has-text("Yes, continue")', { timeout: 5000 }),
      ]).catch(() => null);

      if (authCodeElement) {
        console.error('[gcloud-auth] Found authorization page, clicking approval button...');
        const approveBtn = await page.$('button:has-text("Allow"), button:has-text("Yes, continue")');
        if (approveBtn) {
          await approveBtn.click();
          await page.waitForTimeout(2000);
        }
      }
    } catch (err) {
      console.error('[gcloud-auth] No additional verification needed');
    }

    // Extract authorization code
    console.error('[gcloud-auth] Waiting for authorization code...');
    try {
      // Wait for code display or redirect
      const codePattern = /[a-zA-Z0-9_-]{40,}/;

      // Check page content for code
      const pageText = await page.textContent('body');
      const codeMatch = pageText?.match(codePattern);

      if (codeMatch) {
        authCode = codeMatch[0];
        console.error(`[gcloud-auth] Found authorization code: ${authCode.substring(0, 10)}...`);
      } else {
        // Try to find code in page title or specific elements
        const titleMatch = await page.evaluate(() => document.title).then(title => title.match(codePattern));
        if (titleMatch) {
          authCode = titleMatch[0];
          console.error(`[gcloud-auth] Found code in title: ${authCode.substring(0, 10)}...`);
        }
      }
    } catch (err) {
      console.error(`[gcloud-auth] Error extracting code: ${err.message}`);
    }

    // If we got the code, apply it to gcloud
    if (authCode) {
      console.error(`[gcloud-auth] Successfully extracted authorization code`);

      // Save code to temp file for gcloud to read
      const codePath = path.join(CONFIG.cacheDir, 'auth-code.txt');
      fs.writeFileSync(codePath, authCode, { mode: 0o600 });

      // Output code to stdout for shell capture
      console.log(authCode);

      // Attempt to complete gcloud auth with the code
      const { execSync } = require('child_process');
      try {
        console.error('[gcloud-auth] Submitting authorization code to gcloud...');
        execSync(`echo "${authCode}" | gcloud auth login`, {
          stdio: ['pipe', 'inherit', 'inherit'],
          timeout: 10000,
        });
        console.error('[gcloud-auth] Successfully authenticated with gcloud');
      } catch (err) {
        console.error(`[gcloud-auth] Warning: gcloud auth submission may have failed: ${err.message}`);
        // Still exit successfully since we got the code
      }
    } else {
      console.error('[gcloud-auth] ERROR: Failed to extract authorization code');
      process.exit(1);
    }

    await context.close();
    await browser.close();

  } catch (err) {
    console.error(`[gcloud-auth] Error during authentication: ${err.message}`);
    console.error(err.stack);
    if (browser) await browser.close();
    process.exit(1);
  }
}

// Validate password is provided
if (!CONFIG.password) {
  console.error('[gcloud-auth] ERROR: GCLOUD_AUTH_PASSWORD environment variable not set');
  console.error('[gcloud-auth] Please set your password in secure storage before running this script');
  process.exit(1);
}

// Run authentication
authenticateGCloud().catch(err => {
  console.error('[gcloud-auth] Fatal error:', err);
  process.exit(1);
});
