#!/bin/bash
# Script to clear Google Chrome cache for the default profile on Linux

# Close Chrome before running this script to avoid issues
echo "Closing Google Chrome..."
pkill chrome

# Wait a moment to ensure Chrome is closed
sleep 2

# Path to Chrome cache directory (default profile)
CACHE_DIR="$HOME/.cache/google-chrome/Default/Cache"

if [ -d "$CACHE_DIR" ]; then
  echo "Clearing Chrome cache at $CACHE_DIR"
  rm -rf "$CACHE_DIR"/*
  echo "Chrome cache cleared."
else
  echo "Chrome cache directory not found at $CACHE_DIR"
fi

# Optionally, restart Chrome (uncomment if desired)
# google-chrome &

echo "Done."
