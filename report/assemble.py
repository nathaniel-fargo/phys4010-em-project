#!/usr/bin/env python3
"""
Assemble the final PDF report by combining:
1. Image PDF (full page, no margins)
2. LaTeX report PDF
3. Code PDF (minimal margins)
"""

import subprocess
import sys
from pathlib import Path

try:
    from pypdf import PdfMerger
except ImportError:
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        print("Error: pypdf or PyPDF2 is required. Install with: pip install pypdf")
        sys.exit(1)

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

def convert_image_to_pdf(image_path, output_path):
    """Convert PNG image to full-page PDF with no margins using matplotlib."""
    img = mpimg.imread(str(image_path))
    
    fig = plt.figure(figsize=(8.5, 11), dpi=100)  # Letter size
    ax = fig.add_axes([0, 0, 1, 1])  # Full page, no margins
    ax.imshow(img, aspect='auto', interpolation='nearest')
    ax.axis('off')
    
    with PdfPages(str(output_path)) as pdf:
        pdf.savefig(fig, bbox_inches='tight', pad_inches=0)
    
    plt.close(fig)

def compile_latex(tex_file, output_dir):
    """Compile a LaTeX file to PDF."""
    tex_path = Path(tex_file)
    work_dir = tex_path.parent
    
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', '-output-directory', str(output_dir), str(tex_path)],
        cwd=str(work_dir),
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error compiling {tex_file}:")
        print(result.stdout)
        print(result.stderr)
        return False
    return True

def assemble_pdf(image_pdf, report_pdf, code_pdf, output_pdf):
    """Combine PDFs in order: image, report, code."""
    merger = PdfMerger()
    
    for pdf_file in [image_pdf, report_pdf, code_pdf]:
        if Path(pdf_file).exists():
            merger.append(str(pdf_file))
        else:
            print(f"Warning: {pdf_file} not found, skipping...")
    
    merger.write(str(output_pdf))
    merger.close()

def main():
    # Paths
    report_dir = Path(__file__).parent
    project_dir = report_dir.parent
    build_dir = report_dir / 'build'
    build_dir.mkdir(exist_ok=True)
    
    image_png = project_dir / 'media' / 'multipole_plot.png'
    image_pdf = build_dir / 'image.pdf'
    report_tex = report_dir / 'report.tex'
    report_pdf = build_dir / 'report.pdf'
    code_tex = report_dir / 'code.tex'
    code_pdf = build_dir / 'code.pdf'
    final_pdf = build_dir / 'final_report.pdf'
    
    print("Step 1: Converting image to PDF...")
    if not image_png.exists():
        print(f"Error: Image not found at {image_png}")
        sys.exit(1)
    convert_image_to_pdf(image_png, image_pdf)
    print(f"  Created {image_pdf}")
    
    print("\nStep 2: Compiling main report...")
    if compile_latex(report_tex, build_dir):
        print(f"  Created {report_pdf}")
    else:
        print("  Failed to compile report")
        sys.exit(1)
    
    print("\nStep 3: Compiling code appendix...")
    if compile_latex(code_tex, build_dir):
        print(f"  Created {code_pdf}")
    else:
        print("  Failed to compile code")
        sys.exit(1)
    
    print("\nStep 4: Assembling final PDF...")
    assemble_pdf(image_pdf, report_pdf, code_pdf, final_pdf)
    print(f"  Created {final_pdf}")
    
    print("\nDone! Final report is at:", final_pdf)

if __name__ == '__main__':
    main()

