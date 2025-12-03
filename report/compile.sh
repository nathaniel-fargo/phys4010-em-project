#!/bin/bash

# Compile LaTeX report using pdflatex
# This script compiles report.tex and produces report.pdf in the build/ directory

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the report directory
cd "$SCRIPT_DIR"

# Create build directory if it doesn't exist
mkdir -p build

echo "Compiling report.tex..."
pdflatex -interaction=nonstopmode -output-directory=build report.tex > /dev/null 2>&1

# Run again to resolve any cross-references
pdflatex -interaction=nonstopmode -output-directory=build report.tex > /dev/null 2>&1

echo "Compilation complete! PDF generated: build/report.pdf"

