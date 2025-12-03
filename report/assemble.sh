#!/bin/bash
# Alternative assembly script using command-line tools
# Requires: sips (macOS), pdftk or pdfunite, pdflatex

set -e

REPORT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$REPORT_DIR/.."
BUILD_DIR="$REPORT_DIR/build"
mkdir -p "$BUILD_DIR"

IMAGE_PNG="$PROJECT_DIR/media/multipole_plot.png"
IMAGE_PDF="$BUILD_DIR/image.pdf"
REPORT_TEX="$REPORT_DIR/report.tex"
REPORT_PDF="$BUILD_DIR/report.pdf"
CODE_TEX="$REPORT_DIR/code.tex"
CODE_PDF="$BUILD_DIR/code.pdf"
FINAL_PDF="$BUILD_DIR/final_report.pdf"

echo "Step 1: Converting image to PDF..."
if command -v sips &> /dev/null; then
    # macOS: Use sips to convert PNG to PDF
    sips -s format pdf "$IMAGE_PNG" --out "$IMAGE_PDF" > /dev/null 2>&1
elif command -v convert &> /dev/null; then
    # ImageMagick
    convert "$IMAGE_PNG" -page letter "$IMAGE_PDF"
else
    echo "Error: Need sips (macOS) or ImageMagick convert for image conversion"
    exit 1
fi
echo "  Created $IMAGE_PDF"

echo ""
echo "Step 2: Compiling main report..."
cd "$REPORT_DIR"
if ! pdflatex -interaction=nonstopmode -output-directory "$BUILD_DIR" report.tex > "$BUILD_DIR/report_compile.log" 2>&1; then
    echo "  Error compiling report. Check $BUILD_DIR/report_compile.log"
    exit 1
fi
echo "  Created $REPORT_PDF"

echo ""
echo "Step 3: Compiling code appendix..."
if ! pdflatex -interaction=nonstopmode -output-directory "$BUILD_DIR" code.tex > "$BUILD_DIR/code_compile.log" 2>&1; then
    echo "  Error compiling code. Check $BUILD_DIR/code_compile.log"
    exit 1
fi
echo "  Created $CODE_PDF"

echo ""
echo "Step 4: Assembling final PDF..."
if command -v pdfunite &> /dev/null; then
    pdfunite "$IMAGE_PDF" "$REPORT_PDF" "$CODE_PDF" "$FINAL_PDF"
elif command -v pdftk &> /dev/null; then
    pdftk "$IMAGE_PDF" "$REPORT_PDF" "$CODE_PDF" cat output "$FINAL_PDF"
else
    echo "Error: Need pdfunite or pdftk for PDF merging"
    echo "On macOS, install poppler-utils: brew install poppler"
    exit 1
fi
echo "  Created $FINAL_PDF"

echo ""
echo "Done! Final report is at: $FINAL_PDF"

