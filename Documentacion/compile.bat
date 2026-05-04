@echo off
REM compile.bat — Compila los documentos LaTeX del proyecto DatosAbiertos2026
REM Requiere: MiKTeX o TeX Live con pdflatex y biber en PATH

SET DOC_DIR=%~dp0
SET PROTOCOLO=protocolo-investigacion
SET REPORTE=reporte_investigacion

echo.
echo ============================================
echo  Compilando: %PROTOCOLO%.tex
echo ============================================
cd /d "%DOC_DIR%"

pdflatex -interaction=nonstopmode %PROTOCOLO%.tex
biber %PROTOCOLO%
pdflatex -interaction=nonstopmode %PROTOCOLO%.tex
pdflatex -interaction=nonstopmode %PROTOCOLO%.tex

echo.
echo ============================================
echo  Compilando: %REPORTE%.tex
echo ============================================

pdflatex -interaction=nonstopmode %REPORTE%.tex
biber %REPORTE%
pdflatex -interaction=nonstopmode %REPORTE%.tex
pdflatex -interaction=nonstopmode %REPORTE%.tex

echo.
echo ============================================
echo  Limpiando archivos auxiliares...
echo ============================================
del /Q *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.toc 2>nul

echo.
echo [LISTO] PDFs generados en: %DOC_DIR%
echo  - %PROTOCOLO%.pdf
echo  - %REPORTE%.pdf
pause
