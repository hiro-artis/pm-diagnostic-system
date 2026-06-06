#!/bin/bash

# gcloud-auth-mcp.sh
#
# Wrapper script to automate gcloud authentication using Playwright MCP
# This script is invoked by Claude Code hooks when gcloud auth fails
#
# Usage:
#   ./scripts/gcloud-auth-mcp.sh
#
# Environment Variables:
#   GCLOUD_AUTH_EMAIL - Google account email
#   GCLOUD_AUTH_PASSWORD - Google account password (from secure storage)
#   CLAUDE_MCP_TIMEOUT - Timeout for MCP operations (default: 120s)

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CACHE_DIR="${HOME}/.gcloud-auth-cache"
LOG_FILE="${CACHE_DIR}/gcloud-auth.log"

# Ensure cache directory exists
mkdir -p "$CACHE_DIR"

# Logging function
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting gcloud authentication via Playwright MCP..."

# Step 1: Validate prerequisites
log "Step 1: Validating prerequisites..."

if ! command -v playwright-cli &> /dev/null && ! npm list -g @playwright/test &> /dev/null; then
  log "ERROR: Playwright not found. Installing @playwright/test..."
  npm install -g @playwright/test
fi

if [ -z "${GCLOUD_AUTH_PASSWORD:-}" ]; then
  log "ERROR: GCLOUD_AUTH_PASSWORD not set"
  log "Please store your Google password in secure storage:"
  log "  claude password-manager store GCLOUD_AUTH_PASSWORD"
  exit 1
fi

# Step 2: Launch Playwright automation
log "Step 2: Launching Playwright browser automation..."

AUTH_CODE=""
if [ -f "$SCRIPT_DIR/gcloud-auth-playwright.js" ]; then
  log "Using Node.js Playwright script..."

  # Run the Node script and capture output
  set +e
  AUTH_OUTPUT=$(
    GCLOUD_AUTH_EMAIL="${GCLOUD_AUTH_EMAIL:-hiro@artis-inc.co.jp}" \
    GCLOUD_AUTH_PASSWORD="$GCLOUD_AUTH_PASSWORD" \
    HEADLESS="${GCLOUD_AUTH_HEADLESS:-true}" \
    timeout 120 node "$SCRIPT_DIR/gcloud-auth-playwright.js" 2>&1
  )
  EXIT_CODE=$?
  set -e

  # Extract auth code from output
  AUTH_CODE=$(echo "$AUTH_OUTPUT" | grep -oE '[a-zA-Z0-9_-]{40,}' | head -1 || true)

  log "Playwright script exited with code: $EXIT_CODE"
  if [ $EXIT_CODE -eq 124 ]; then
    log "ERROR: Playwright script timeout after 120 seconds"
    exit 1
  fi
else
  log "ERROR: Playwright script not found at $SCRIPT_DIR/gcloud-auth-playwright.js"
  exit 1
fi

# Step 3: Validate auth code
log "Step 3: Validating authorization code..."

if [ -z "$AUTH_CODE" ]; then
  log "ERROR: Failed to extract authorization code from Playwright output"
  log "Output was:"
  echo "$AUTH_OUTPUT" | head -20 >> "$LOG_FILE"
  exit 1
fi

log "Successfully extracted authorization code: ${AUTH_CODE:0:10}..."

# Step 4: Apply auth code to gcloud
log "Step 4: Applying authorization code to gcloud CLI..."

if command -v gcloud &> /dev/null; then
  set +e
  GCLOUD_OUTPUT=$(echo "$AUTH_CODE" | gcloud auth login 2>&1)
  GCLOUD_EXIT_CODE=$?
  set -e

  if [ $GCLOUD_EXIT_CODE -eq 0 ]; then
    log "Successfully authenticated with gcloud"
  else
    log "WARNING: gcloud auth may have partially failed (exit code: $GCLOUD_EXIT_CODE)"
    log "However, the authorization code was extracted successfully"
  fi
else
  log "WARNING: gcloud CLI not found in PATH"
  log "Auth code saved to: $CACHE_DIR/auth-code.txt"
  echo "$AUTH_CODE" > "$CACHE_DIR/auth-code.txt"
  chmod 600 "$CACHE_DIR/auth-code.txt"
fi

# Step 5: Verify authentication
log "Step 5: Verifying gcloud authentication..."

set +e
gcloud auth list 2>&1 | head -5 >> "$LOG_FILE"
set -e

log "gcloud authentication workflow completed successfully"
echo "AUTHENTICATION_SUCCESSFUL"
