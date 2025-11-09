#!/bin/bash
set -e

# --- 1. Define Persistent Directory on the Render Disk ---
# This is the directory that persists across restarts and deploys.
PERSISTENT_DIR="/mnt/data/camoufox"

# --- 2. Conditional Check ---
# Check if a critical file (e.g., the main executable) already exists on the disk.
# If it exists, skip the entire download/extraction process.
if [ -f "$PERSISTENT_DIR/camoufox-142.0.1-fork.26-lin.x86_64/firefox" ]; then
    echo "Camoufox installation found on disk ($PERSISTENT_DIR). Skipping download and extraction."
    exit 0
fi

echo "Camoufox not found on disk. Starting fresh installation..."
mkdir -p "$PERSISTENT_DIR"

# --- 3. Installation Steps (First Time Only) ---

# Camoufox Download (Large File)
CAMOUFOX_URL="https://github.com/coryking/camoufox/releases/download/v142.0.1-fork.26/camoufox-142.0.1-fork.26-lin.x86_64.zip"
CAMOUFOX_ZIP="/tmp/camoufox.zip" # Download temporarily to fast, non-persistent storage

echo "Downloading package: $CAMOUFOX_URL"
curl -L -o "$CAMOUFOX_ZIP" "$CAMOUFOX_URL"

echo "Extracting Camoufox to persistent disk: $PERSISTENT_DIR"
# The zip contains a directory, so extract it into the persistent directory
unzip -q "$CAMOUFOX_ZIP" -d "$PERSISTENT_DIR"

# Clean up the large zip file
rm "$CAMOUFOX_ZIP"
echo "Camoufox successfully installed and saved to disk."

# NOTE: Add the download logic for model files and addons here,
# ensuring they also land within the $PERSISTENT_DIR.