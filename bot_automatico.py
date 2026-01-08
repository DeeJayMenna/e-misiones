import csv
import json
import urllib.request
import io
import os
import feedparser
from datetime import datetime

# ==========================================
# CONFIGURACIÓN
# ==========================================

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRXyaaH8eahCWIWJ96eqkwhekAbZMxP6SwYL9lbq8SJSWU3kqmNeW05dXpSwH-3sMJt7UX1vRSjdmVD/pub?gid=360992990&single=true&output=csv"

FUENTES_RSS = [
    # --- LOCALES (MISIONES) ---
    {
        "nombre": "MisionesOnline",
        "url": "https://misionesonline.net/feed/",
        "categoria": "Noticia Local",
        "limite": 3
    },
    {
        "nombre": "El Territorio",
        "url": "https://www.elterritorio.com.ar/rss/home", 
        "categoria": "Noticia Local",
        "limite": 3
    },
    {
        "nombre": "Primera Edición",
        "url": "https://www.primeraedicion.com.ar/feed/",
        "categoria": "Noticia Local",
        "limite": 3
    },
    # --- NACIONALES ---
    {
        "nombre": "La Nación",
        "url": "https://www.lanacion.com.ar/arc/outboundfeeds/rss/?outputType=xml",
        "categoria": "Noticia Nacional",
        "limite": 2
    },
    {
        "nombre": "Clarín",
        "url": "https://www.clarin.com/rss/lo-ultimo/",
        "categoria": "Noticia Nacional",
        "limite": 2
    },
    # --- TU AGREGADO (CORREGIDO) ---
    {
        "nombre": "La 100",
        # El link que pusiste era la web visual. Este es el técnico RSS:
        "url": "https://la100.cienradios.com/arc/outboundfeeds/rss/", 
        "categoria": "Noticia Nacional",
        "limite": 2
    }
]

ARCHIVO_DESTINO = os.path.join("static", "datos.js")

MAPA_MESES = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

# ==========================================
# FUNCIONES
# ==========================================
def obtener_efemerides_sheet():
    print("⏳ [1/3] Leyendo Google Sheets...")
    lista_sheet = []
    try:
        response = urllib.request.urlopen(SHEET_URL)
        csv_data = response.read().decode('utf-8')
        lector = csv.DictReader(io.StringIO(csv_data))
        
        for fila in lector:
            # Búsqueda flexible de columnas
            dia_raw = None
            for key in fila: 
                if "DIA" in key.upper() or "DÍA" in key.upper(): dia_raw = fila[key]; break
            
            mes_raw = None
            for key in fila: 
                if "MES" in key.upper(): mes_raw = fila[key]; break

            anio_raw = None
            for key in fila:
                if "AÑO" in key.upper() or "ANIO" in key.upper(): anio_raw = fila[key]; break
                
            titulo_raw = None
            for key in fila:
                if "TITULO" in key.upper() or "TÍTULO" in key.upper(): titulo_raw = fila[key]; break

            cat_raw = None
            for key in fila:
                if "CATEGOR" in key.upper() or "TIPO" in key.upper() or "TÍPO" in key.upper(): cat_raw = fila[key]; break

            desc_raw = None
            for key in fila:
                if "DESC" in key.upper() or "CONTENIDO" in key.upper(): desc_raw = fila[key]; break

            if dia_raw and mes_raw:
                try:
                    dia = int(str(dia_raw).strip())
                    mes_str = str(mes_raw).strip().lower()
                    mes = int(mes_str) if mes_str.isdigit() else MAPA_MESES.get(mes_str, 0)
                    
                    if dia > 0 and mes > 0:
                        lista_sheet.append({
                            "dia": dia,
                            "mes": mes,
                            "anio": str(anio_raw).strip(),
                            "titulo": str(titulo_raw).strip(),
                            "categoria": str(cat_raw).strip(),
                            "descripcion": str(desc_raw).strip()
                        })
                except:
                    continue
        print(f"   ✅ Efemérides encontradas: {len(lista_sheet)}")
        return lista_sheet
    except Exception as e:
        print(f"   ❌ Error leyendo Google Sheets: {e}")
        return []

def obtener_noticias_rss():
    print("⏳ [2/3] Descargando Noticias RSS...")
    lista_noticias = []
    hoy = datetime.now()
    
    for fuente in FUENTES_RSS:
        try:
            feed = feedparser.parse(fuente['url'])
            
            # --- CHIVATO DE DEPURACIÓN ---
            cantidad = len(feed.entries)
            if cantidad == 0:
                print(f"   ⚠️  {fuente['nombre']}: 0 noticias (Revisar Enlace RSS)")
            else:
                print(f"   ✅ {fuente['nombre']}: {cantidad} noticias encontradas")
            # -----------------------------

            contador = 0
            for entrada in feed.entries:
                if contador >= fuente['limite']:
                    break
                
                resumen = entrada.summary if 'summary' in entrada else ""
                resumen = resumen.replace("<p>", "").replace("</p>", "").replace("&nbsp;", " ")
                if len(resumen) > 160:
                    resumen = resumen[:160] + "..."

                html_descripcion = f"{resumen}<br><br><a href='{entrada.link}' target='_blank' style='color:#2563eb; font-weight:bold;'>Leer en {fuente['nombre']} <i class='fas fa-external-link-alt'></i></a>"

                noticia_item = {
                    "dia": hoy.day,
                    "mes": hoy.month,
                    "anio": hoy.year,
                    "titulo": entrada.title,
                    "categoria": fuente['categoria'],
                    "descripcion": html_descripcion
                }
                
                lista_noticias.append(noticia_item)
                contador += 1
                
        except Exception as e:
            print(f"   ❌ Error crítico con {fuente['nombre']}: {e}")
            continue

    return lista_noticias

def generar_base_de_datos():
    datos_sheet = obtener_efemerides_sheet()
    datos_rss = obtener_noticias_rss()
    
    datos_totales = datos_rss + datos_sheet
    
    contenido_js = f"const BASE_DE_DATOS = {json.dumps(datos_totales, indent=4, ensure_ascii=False)};"
    
    try:
        with open(ARCHIVO_DESTINO, "w", encoding="utf-8") as f:
            f.write(contenido_js)
        print("="*50)
        print(f"🎉 [3/3] FINALIZADO. Total eventos hoy: {len(datos_totales)}")
        print(f"📂 Archivo guardado en: {ARCHIVO_DESTINO}")
        print("👉 IMPORTANTE: Recarga tu web con CTRL + F5")
        print("="*50)
    except Exception as e:
        print(f"❌ Error guardando archivo: {e}")

if __name__ == "__main__":
    generar_base_de_datos()