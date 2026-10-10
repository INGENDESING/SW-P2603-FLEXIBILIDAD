# Script de compilacion automatizada limpia para entorno Windows
# Evita que el directorio raiz de LaTeX se llene de archivos auxiliares
#
# USO:
#   .\compilar_informe.ps1              # Usa valor por defecto de $jobName
#   .\compilar_informe.ps1 -jobName "PXXXX-PR-INF-001"
#
# CONFIGURACION:
#   Modifique la variable $jobNameDefault con el codigo de su proyecto.

param(
    [string]$jobName = "DOCUMENTO"
)

Write-Host "Iniciando compilacion limpia de pdflatex..." -ForegroundColor Cyan
Write-Host "Nombre del trabajo: $jobName" -ForegroundColor Cyan

# Verifica si la carpeta build existe, de lo contrario la crea
if (!(Test-Path "build")) {
    New-Item -ItemType Directory -Force -Path "build" | Out-Null
}

# Compila redirigiendo auxiliares y PDF a la subcarpeta build
pdflatex -jobname="$jobName" -interaction=nonstopmode -output-directory=build main.tex

# Compila segunda vez para asegurar referencias (TOC, LOT, LOF) cruzadas completas
pdflatex -jobname="$jobName" -interaction=nonstopmode -output-directory=build main.tex

# Reubica el PDF resultante desde la carpeta de build a la raiz del informe para facil acceso
if (Test-Path "build\$jobName.pdf") {
    Copy-Item "build\$jobName.pdf" -Destination "$jobName.pdf" -Force
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "Exito! PDF principal actualizado y todos los logs fueron ocultados en /build" -ForegroundColor Green
}
else {
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "Error en la compilacion. Revisa build/$jobName.log" -ForegroundColor Red
}
