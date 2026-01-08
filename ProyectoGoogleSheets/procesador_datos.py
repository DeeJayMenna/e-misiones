import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import re
import time
import os

# --- 1. CONFIGURACIÓN ROBUSTA DE RUTAS ---
# Esto asegura que sepamos exactamente dónde estamos parados
DIRECTORIO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RUTA_CREDENCIALES = os.path.join(DIRECTORIO_SCRIPT, "credentials.json")
RUTA_SALIDA_JSON = os.path.join(DIRECTORIO_SCRIPT, "efemerides.json")

def conectar_google_sheets(nombre_archivo_sheet):
    print(f"   > Buscando credenciales en: {RUTA_CREDENCIALES}")
    
    if not os.path.exists(RUTA_CREDENCIALES):
        print("   [ERROR CRÍTICO] No encuentro el archivo credentials.json")
        return None

    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    try:
        creds = Credentials.from_service_account_file(RUTA_CREDENCIALES, scopes=scopes)
        client = gspread.authorize(creds)
        print(f"   > Intentando abrir la hoja: '{nombre_archivo_sheet}'...")
        spreadsheet = client.open(nombre_archivo_sheet)
        print("   [OK] ¡Conexión exitosa con el archivo!")
        return spreadsheet
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"   [ERROR] No encontré el archivo '{nombre_archivo_sheet}' en tu Google Drive.")
        print("   [PISTA] Revisa mayúsculas, tildes o espacios en el nombre.")
        return None
    except Exception as e:
        print(f"   [ERROR] Ocurrió otro error: {e}")
        return None

# --- 2. LÓGICA DE PROCESAMIENTO ---

def generar_tags_y_categoria(texto, titulo):
    texto_completo = (str(titulo) + " " + str(texto)).lower()
    tags = []
    categoria_geo = "Internacional"

    keywords = {
        "#deporte": ["futbol", "club", "atletico", "funda el equipo", "copa", "deporte", "galaxy", "torneo"],
        "#sociedad": ["paz", "hijo", "educación", "salud", "niñez", "mujer", "derechos"],
        "#historia": ["fundación", "batalla", "guerra", "independencia", "creación", "imperio", "disolución", "revolución"],
        "#ciencia": ["descubrimiento", "nasa", "espacio", "inventó", "científico", "tecnología"],
        "#cultura": ["arte", "música", "libro", "publica", "canción", "cine", "película"]
    }

    for tag, palabras in keywords.items():
        if any(p in texto_completo for p in palabras):
            tags.append(tag)

    if "argentina" in texto_completo or "buenos aires" in texto_completo or "independiente" in texto_completo:
        categoria_geo = "Nacional"
        tags.append("#argentina")
    
    if "día de" in texto_completo or "día internacional" in texto_completo or "día mundial" in texto_completo:
        tags.append("#díade")
        tags.append("#celebración")

    return categoria_geo, ", ".join(set(tags))

def procesar_texto_crudo(contenido_celda, dia, mes_nombre):
    filas_procesadas = []
    if not contenido_celda: return []
    
    lineas = str(contenido_celda).split('\n')
    for linea in lineas:
        linea = linea.strip()
        if not linea: continue

        anio_evento = ""
        titulo = ""
        descripcion = ""
        tipo = ""

        patron = r"^(\d{4})\s*-\s*(.*?)\.\s*(.*)$"
        match = re.match(patron, linea)

        if match:
            anio_evento = match.group(1)
            titulo = match.group(2).strip()
            descripcion = match.group(3).strip()
            tipo = "Efeméride Histórica"
            if not descripcion: descripcion = titulo
        else:
            anio_evento = "" 
            titulo = linea.replace(".", "")
            descripcion = "Celebración del " + titulo
            tipo = "Celebración"

        cat_geo, tags = generar_tags_y_categoria(descripcion, titulo)

        fila = {
            'DIA': dia,
            'MES': mes_nombre,
            'ANIO_EVENTO': anio_evento,
            'TITULO': titulo,
            'DESCRIPCION': descripcion,
            'CATEGORIA': f"{tipo} - {cat_geo}",
            'TAGS': tags
        }
        filas_procesadas.append(fila)
    return filas_procesadas

def obtener_efemerides_actualizadas(nombre_sheet):
    spreadsheet = conectar_google_sheets(nombre_sheet)
    if not spreadsheet: return pd.DataFrame()

    todos_los_datos = []
    hojas = spreadsheet.worksheets()
    print(f"   > Procesando {len(hojas)} pestañas (hojas)...")

    for worksheet in hojas:
        columna_a = worksheet.col_values(1)
        for i, contenido_celda in enumerate(columna_a):
            dia_numero = i + 1
            if dia_numero > 31: break 
            nuevas_filas = procesar_texto_crudo(contenido_celda, dia_numero, worksheet.title)
            todos_los_datos.extend(nuevas_filas)
        time.sleep(0.5)

    df = pd.DataFrame(todos_los_datos)
    if not df.empty:
        columnas = ['DIA', 'MES', 'ANIO_EVENTO', 'TITULO', 'DESCRIPCION', 'CATEGORIA', 'TAGS']
        for col in columnas:
            if col not in df.columns: df[col] = ""
        df = df[columnas]
    
    return df

# --- 3. EJECUCIÓN ---

if __name__ == "__main__":
    print("\n--- INICIANDO SCRIPT DETECTIVE ---")
    
    # !!! REVISA ESTE NOMBRE !!!
    NOMBRE_HOJA = "Efemerides" 
    
    df_efemerides = obtener_efemerides_actualizadas(NOMBRE_HOJA)
    
    print("\n--- RESULTADO DEL PROCESO ---")
    if not df_efemerides.empty:
        print(f"   [OK] Se obtuvieron {len(df_efemerides)} registros.")
        
        # Guardar forzosamente en la misma carpeta que el script
        try:
            df_efemerides.to_json(RUTA_SALIDA_JSON, orient='records', force_ascii=False, indent=4)
            print(f"   [ÉXITO TOTAL] Archivo creado en: {RUTA_SALIDA_JSON}")
            print("   -> Búscalo en esa carpeta.")
        except Exception as e:
            print(f"   [ERROR AL GUARDAR] No se pudo escribir el archivo: {e}")
            
    else:
        print("   [FALLO] No se encontraron datos para guardar.")
        print("   POSIBLES CAUSAS:")
        print("   1. El nombre 'Efemérides Data Master' no coincide con tu Google Sheet.")
        print("   2. El archivo de Google Sheet está vacío.")
        print("   3. Falló la conexión (mira los mensajes de arriba).")