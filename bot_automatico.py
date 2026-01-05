import time
import os
import subprocess
from datetime import datetime
import actualizar  # Importamos tu script de noticias

# ==========================================
# CONFIGURACIÓN
# ==========================================
TIEMPO_ESPERA = 1800  # 30 minutos en segundos
RAMA_GITHUB = "main"  # Tu rama principal se llama 'main'

def subir_a_github():
    print("🚀 Subiendo cambios a GitHub...")
    try:
        # 1. Agregar todos los archivos
        subprocess.run(["git", "add", "."], check=True)
        
        # 2. Guardar cambios (Commit)
        hora = datetime.now().strftime("%H:%M")
        mensaje = f"Actualización automática: {hora}"
        subprocess.run(["git", "commit", "-m", mensaje], check=True)
        
        # 3. Empujar a la nube (Push)
        subprocess.run(["git", "push", "origin", RAMA_GITHUB], check=True)
        print("✅ ¡GitHub actualizado con éxito!")
        
    except subprocess.CalledProcessError:
        print("⚠️ No hubo cambios nuevos para subir o falló la conexión.")
    except Exception as e:
        print(f"❌ Error desconocido en Git: {e}")

def iniciar_ciclo():
    print("🤖 BOT AUTOMÁTICO INICIADO - e-misiones")
    print(f"   Se actualizará cada {TIEMPO_ESPERA/60} minutos.")
    print("   (Presiona CTRL + C para detenerlo)")
    print("="*50)

    while True:
        hora_inicio = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{hora_inicio}] 🔄 Buscando noticias nuevas...")

        # PASO 1: ACTUALIZAR NOTICIAS
        try:
            actualizar.generar_base_de_datos()
        except Exception as e:
            print(f"❌ Error en el script de noticias: {e}")

        # PASO 2: SUBIR A GITHUB
        subir_a_github()

        # PASO 3: ESPERAR
        proxima = datetime.now().strftime('%H:%M')
        print(f"💤 Durmiendo... Próxima revisión en 30 minutos.")
        time.sleep(TIEMPO_ESPERA)

if __name__ == "__main__":
    iniciar_ciclo()