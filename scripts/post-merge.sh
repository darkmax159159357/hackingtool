#!/bin/bash
set -e

pip install -q flask requests colorama fuzzywuzzy tldextract 2>/dev/null || true

echo "Post-merge setup complete"
