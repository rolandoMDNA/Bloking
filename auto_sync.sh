#!/bin/bash

# Este script sincroniza automáticamente los cambios a GitHub
# cada vez que detecta modificaciones en el proyecto.

WATCH_DIR="/home/rolandomdna/.gemini/antigravity/scratch/bloking"
cd "$WATCH_DIR" || exit

echo "[*] Sincronización automática iniciada para $WATCH_DIR"
echo "[*] Usa 'Ctrl+C' para detener."

while true; do
    # Verifica si hay cambios usando git status
    if [[ -n $(git status -s) ]]; then
        echo -e "\n[+] Cambios detectados. Sincronizando con GitHub..."
        git add .
        git commit -m "Auto-sync $(date +'%Y-%m-%d %H:%M:%S')"
        git push
        echo "[✓] ¡Sincronizado!"
    fi
    sleep 5
done
