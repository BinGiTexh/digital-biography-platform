#!/usr/bin/env bash
# Sync CoralScapes screenshots from Jetson device to local ~/portfolio
# Usage: ./scripts/jetson/sync_portfolio.sh

set -euo pipefail

JETSON_HOST="mza-bingi@bingilab-agx"
REMOTE_DIR="~/coralscapes/output"
LOCAL_DIR="$HOME/portfolio"

echo "🔗 Syncing portfolio images from $JETSON_HOST:$REMOTE_DIR -> $LOCAL_DIR"
mkdir -p "$LOCAL_DIR"

# Only pull new/updated PNG & JPG files
rsync -avz --progress --include='*/' --include='*.png' --include='*.jpg' --include='*.jpeg' --exclude='*' \
    "$JETSON_HOST:$REMOTE_DIR/" "$LOCAL_DIR/"

echo "✅ Sync complete"
