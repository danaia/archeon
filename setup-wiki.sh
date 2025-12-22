#!/bin/bash

# Archeon Wiki Setup Script
# This script initializes and populates the GitHub wiki for the Archeon repository

set -e  # Exit on error

REPO_OWNER="danaia"
REPO_NAME="Archeon"
WIKI_DIR="wiki"
TEMP_WIKI_DIR="wiki-temp"

echo "🚀 Archeon Wiki Setup"
echo "===================="
echo ""

# Check if wiki files exist
if [ ! -d "$WIKI_DIR" ]; then
    echo "❌ Error: wiki/ directory not found"
    echo "   Expected wiki pages in: $WIKI_DIR/"
    exit 1
fi

# Count wiki pages
WIKI_COUNT=$(find "$WIKI_DIR" -name "*.md" | wc -l | tr -d ' ')
echo "📄 Found $WIKI_COUNT wiki pages in $WIKI_DIR/"
echo ""

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI detected"
    USE_GH_CLI=true
else
    echo "⚠️  GitHub CLI not found (install with: brew install gh)"
    USE_GH_CLI=false
fi

echo ""
echo "📡 Checking if wiki exists..."

# Try to clone the wiki
if git clone "https://github.com/$REPO_OWNER/$REPO_NAME.wiki.git" "$TEMP_WIKI_DIR" 2>/dev/null; then
    echo "✅ Wiki repository exists"
else
    echo "⚠️  Wiki doesn't exist yet"
    echo ""
    echo "GitHub wikis must be initialized manually the first time."
    echo ""
    echo "📋 Quick setup steps:"
    echo ""
    echo "   1. Open: https://github.com/$REPO_OWNER/$REPO_NAME/wiki"
    echo ""
    echo "   2. Click the green 'Create the first page' button"
    echo ""
    echo "   3. Enter anything for title and content (it will be replaced)"
    echo "      For example:"
    echo "      Title: Home"
    echo "      Content: Archeon Framework Documentation"
    echo ""
    echo "   4. Click 'Save Page'"
    echo ""
    echo "   5. Run this script again: ./setup-wiki.sh"
    echo ""
    exit 1
fi

echo ""
echo "📦 Copying wiki pages..."

# Copy all markdown files
cp -v "$WIKI_DIR"/*.md "$TEMP_WIKI_DIR/"

cd "$TEMP_WIKI_DIR"

echo ""
echo "📝 Committing changes..."

git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✅ No changes detected - wiki is already up to date"
    cd ..
    rm -rf "$TEMP_WIKI_DIR"
    echo ""
    echo "🎉 Done! Wiki is current."
    exit 0
fi

git commit -m "Add comprehensive Archeon framework documentation

- Home page with navigation
- Installation guide
- Quick Start tutorial
- Glyph Reference (16 glyph types)
- Chain Syntax guide
- CLI Commands reference
- Templates guide
- Architecture guide"

echo ""
echo "🚀 Pushing to GitHub..."

git push origin master

cd ..

# Cleanup
echo ""
echo "🧹 Cleaning up..."
rm -rf "$TEMP_WIKI_DIR"

echo ""
echo "✅ Wiki successfully published!"
echo "🌐 View at: https://github.com/$REPO_OWNER/$REPO_NAME/wiki"
echo ""
