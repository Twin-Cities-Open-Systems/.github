#!/usr/bin/env bash
# Automated Multi-Gate Pre-Commit Driver for TCOS

set -e
"${HOME}/git/.github/bin/hooks/pre-commit-link-check.sh"
"${HOME}/git/.github/bin/hooks/pre-commit-secret-check.sh"
