pdflatex --shell-escape --interaction=nonstopmode report
bibtex report
pdflatex --shell-escape --interaction=nonstopmode report
pdflatex --shell-escape --interaction=nonstopmode report
open report.pdf