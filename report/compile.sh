pdflatex --shell-escape --interaction=nonstopmode report
biber report
pdflatex --shell-escape --interaction=nonstopmode report
pdflatex --shell-escape --interaction=nonstopmode report
open report.pdf