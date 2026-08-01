#!/bin/bash
set -e

echo "=== QuickBucks Deploy Script ==="
echo ""

# Deploy affiliate blog to Surge
echo "[1/2] Deploying affiliate blog..."
npx surge /home/dodontommy/quickbucks/affiliate-blog/ vpnreviews-2026.surge.sh 2>/dev/null || {
  echo "  Surge not available. Deploy manually:"
  echo "  1. Go to https://github.com/dodontommy/vpnreviews-blog/settings/pages"
  echo "  2. Set branch=master, folder=/ (root)"
}

echo "[2/2] Deploying data broker site..."
npx surge /home/dodontommy/quickbucks/data-broker/site/ h1b-data-2026.surge.sh 2>/dev/null || {
  echo "  Surge not available. Deploy manually:"
  echo "  1. Go to https://github.com/dodontommy/h1b-data-broker/settings/pages"
  echo "  2. Set branch=master, folder=/ (root)"
}

echo ""
echo "Done! Update your affiliate links in affiliate-blog/index.html"
echo "Then push to GitHub to auto-deploy Pages."