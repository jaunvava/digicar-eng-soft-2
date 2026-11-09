#!/usr/bin/env bash
# Compila e executa o Sistema de Pagamentos (Linux / macOS / Git Bash)
set -e
cd "$(dirname "$0")"
rm -rf out
javac -encoding UTF-8 -d out $(find src -name "*.java")
java -cp out pagamentos.app.Main
