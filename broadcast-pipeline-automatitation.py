#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER PIPELINE — PLECA VERDE → PLECA ZU → BACK → GS → FIX iPLAY
Versión final corregida, limpia, consistente y producción-ready.
"""

import os
import re
import subprocess
import unicodedata
import time
from datetime import datetime
import openpyxl

# ==============================================================================
# CONFIGURACIÓN GENERAL
# ==============================================================================

FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"
NATRON_RENDERER = r"C:\Program Files\Natron\bin\NatronRenderer.exe"

CARPETA_SALIDA = r"C:\NatronProject\Programa_hoy"
CARPETA_ZU     = r"C:\NatronProject\Materiales\Pleca"

os.makedirs(CARPETA_SALIDA, exist_ok=True)
os.makedirs(CARPETA_ZU, exist_ok=True)

# Plantillas Natron
PLANTILLA_PLECA_VERDE = r"C:\NatronProject\Pleca-720.ntp"
PLANTILLA_PLECA_ZU    = r"C:\NatronProject\NatronPlantillas\PlecaBack-720.ntp"
PLANTILLA_GS          = r"C:\NatronProject\Greenscreen-720.ntp"

# Back y blur
BACKLOGO_KEYED = r"C:\NatronProject\Base\mov\Back.mov"
BACKBLUR       = r"C:\NatronProject\Base\BackBlur-720.png"

# Excel
EXCEL_RUTA  = r"C:\NatronProject\Materiales\RFPauta-diaria.xlsx"
EXCEL_HOJA  = "Hoja1"
EXCEL_COL   = "B"
FILA_INICIO = 2

# Notas
NOTAS = [
    r"C:\NatronProject\Materiales\Videos\nota{:02d}.mp4".format(i)
    for i in range(1, 8)
]

# GS
LASTFRAME_GS = 720
LASTFRAME_ZU = 12 * 24  # 12 segundos a 24fps

# Tiempo global
INICIO_GLOBAL = time.time()

# ==============================================================================
# UTILIDADES
# ==============================================================================

def log(msg):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)

def run_silencioso(cmd):
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def limpiar_titulo(t):
    t = re.sub(r'[\\/*?:"<>|]', "", t)
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", "_", t).strip()

def cargar_titulos():
    wb = openpyxl.load_workbook(EXCEL_RUTA, data_only=True)
    sh = wb[EXCEL_HOJA]
    titulos = []
    fila = FILA_INICIO
    while True:
        v = sh[f"{EXCEL_COL}{fila}"].value
        if v is None:
            break
        titulos.append(str(v).strip())
        fila += 1
    wb.close()
    return titulos

def get_duracion(path):
    p = subprocess.run([
        FFPROBE, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode().strip()
    return float(out) if out else None

def generar_backblur(video):
    run_silencioso([
        FFMPEG, "-y",
        "-i", video,
        "-vf", "scale=1280:720, gblur=sigma=25",
        "-frames:v", "1",
        BACKBLUR
    ])

def tiempo_legible(segundos):
    minutos = int(segundos // 60)
    segs = int(segundos % 60)
    return f"{minutos} min {segs} s"

# ==============================================================================
# CONFIGURACIÓN GS (VIDEOS + IMÁGENES)
# ==============================================================================
#
MATERIALES_ARCHIVOS = [
    (r"C:\NatronProject\Materiales\Videos\nota01.mp4", r"C:\NatronProject\Materiales\Imagenes\gs01.jpg"),
    (r"C:\NatronProject\Materiales\Videos\nota02.mp4", r"C:\NatronProject\Materiales\Imagenes\gs02.jpg"),
    (r"C:\NatronProject\Materiales\Videos\nota03.mp4", r"C:\NatronProject\Materiales\Imagenes\gs03.jpg"),
    (r"C:\NatronProject\Materiales\Videos\nota04.mp4", r"C:\NatronProject\Materiales\Imagenes\gs04.jpg"),
    (r"C:\NatronProject\Materiales\Videos\nota05.mp4", r"C:\NatronProject\Materiales\Imagenes\gs05.jpg"),
    (r"C:\NatronProject\Materiales\Videos\nota06.mp4", r"C:\NatronProject\Materiales\Imagenes\gs06.jpg"),
    (r"C:\NatronProject\Materiales\Videos\nota07.mp4", r"C:\NatronProject\Materiales\Imagenes\gs07.jpg"),
]

def construir_datos_notas(titulos):
    return [
        (video, imagen, titulo)
        for (video, imagen), titulo in zip(MATERIALES_ARCHIVOS, titulos)
    ]

# ==============================================================================
# FASE 1 — PLECA VERDE
# ==============================================================================

def fase_pleca_verde(titulos):
    log("=== FASE 1 — PLECA VERDE ===")
    plantilla = open(PLANTILLA_PLECA_VERDE, "r", encoding="utf-8").read()

    for i, titulo in enumerate(titulos, start=1):
        inicio = time.time()
        titulo_limpio = limpiar_titulo(titulo)

        salida = os.path.join(CARPETA_SALIDA, f"{i:02d}_ZU_{titulo_limpio}.mp4")
        temp   = os.path.join(CARPETA_SALIDA, f"temp_pv_{i}.ntp")

        log(f"[PLECA VERDE] {i:02d} — {titulo}")

        open(temp, "w", encoding="utf-8").write(
            plantilla.replace("CAMBIAR_TEXTO", titulo)
        )

        run_silencioso([NATRON_RENDERER, "-b", "-w", "Write1", salida, temp])
        os.remove(temp)

        log(f"   ✔ OK ({time.time() - inicio:.2f}s)")

# ==============================================================================
# FASE 2 — PLECA ZU
# ==============================================================================

def fase_pleca_zu(titulos):
    log("=== FASE 2 — PLECA ZU ===")
    plantilla = open(PLANTILLA_PLECA_ZU, "r", encoding="utf-8").read()

    for i, titulo in enumerate(titulos, start=1):
        inicio = time.time()
        titulo_limpio = limpiar_titulo(titulo)

        salida = os.path.join(CARPETA_ZU, f"{i:02d}_ZU_{titulo_limpio}.mov")
        temp   = os.path.join(CARPETA_ZU, f"temp_pzu_{i}.ntp")

        log(f"[PLECA ZU] {i:02d} — {titulo}")

        ntp = plantilla.replace("CAMBIAR_TEXTO", titulo)
        ntp = re.sub(r"lastFrame\s*=\s*\d+", f"lastFrame = {LASTFRAME_ZU}", ntp)

        open(temp, "w", encoding="utf-8").write(ntp)

        run_silencioso([NATRON_RENDERER, "-b", "-w", "Write1", salida, temp])
        os.remove(temp)

        log(f"   ✔ OK ({time.time() - inicio:.2f}s)")

# ==============================================================================
# FASE 3 — BACK
# ==============================================================================

def fase_back(titulos):
    log("=== FASE 3 — BACK ===")

    for i, video in enumerate(NOTAS, start=1):
        if i > len(titulos):
            break

        inicio = time.time()
        titulo = titulos[i-1]
        titulo_limpio = limpiar_titulo(titulo)

        salida = os.path.join(CARPETA_SALIDA, f"{i:02d}_SO_{titulo_limpio}.mp4")
        zu     = os.path.join(CARPETA_ZU, f"{i:02d}_ZU_{titulo_limpio}.mov")

        log(f"[BACK] {i:02d} — {titulo}")

        dur = get_duracion(video)
        generar_backblur(video)

        filtro = (
            "[0:v]scale=1280:720, gblur=sigma=25[bg];"
            "[0:v]scale=-2:720[nota720];"
            "[bg][nota720]overlay=(1280-w)/2:(720-h)/2[nota_comp];"
            "[1:v]scale=1280:720[back720];"
            f"[2:v]tpad=stop_mode=clone:stop_duration={dur}[zu_raw];"
            "[zu_raw]scale=1280:720[zu720];"
            "[nota_comp][back720]overlay=0:0[step1];"
            "[step1][zu720]overlay=0:0[final]"
        )

        run_silencioso([
            FFMPEG, "-y",
            "-i", video,
            "-i", BACKLOGO_KEYED,
            "-i", zu,
            "-filter_complex", filtro,
            "-map", "[final]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-shortest",
            "-t", f"{dur}",
            salida
        ])

        log(f"   ✔ OK ({time.time() - inicio:.2f}s)")

# ==============================================================================
# FASE 4 — GS
# ==============================================================================

def fase_gs(titulos):
    log("=== FASE 4 — GS ===")

    plantilla = open(PLANTILLA_GS, "r", encoding="utf-8").read()
    datos = construir_datos_notas(titulos)

    for i, (video, img, titulo) in enumerate(datos, start=1):
        inicio = time.time()
        titulo_limpio = limpiar_titulo(titulo)

        salida = os.path.join(CARPETA_SALIDA, f"{i:02d}_GS_{titulo_limpio}.mp4")
        temp   = os.path.join(CARPETA_SALIDA, f"temp_gs_{i}.ntp")

        log(f"[GS] {i:02d} — {titulo}")

        ntp = plantilla.replace("CAMBIAR_TEXTO", titulo)
        ntp = ntp.replace("TEXTO_PLECA", titulo)
        ntp = re.sub(r"lastFrame\s*=\s*\d+", f"lastFrame = {LASTFRAME_GS}", ntp)

        img_esc = img.replace("\\", "/")
        ntp = re.sub(
            r'(<Plugin_label>Read2</Plugin_label>[\s\S]*?<Name>filename</Name>[\s\S]*?<Value>)(.*?)(</Value>)',
            rf'\1{img_esc}\3',
            ntp
        )

        open(temp, "w", encoding="utf-8").write(ntp)

        run_silencioso([NATRON_RENDERER, "-b", "-w", "Write1", salida, temp])
        os.remove(temp)

        log(f"   ✔ OK ({time.time() - inicio:.2f}s)")

# ==============================================================================
# FASE 5 — REEXPORTACIÓN BROADCAST-SAFE PARA iPLAY
# ==============================================================================

def fase_fix_iplay():
    log("\n=== FASE 5 — REEXPORT iPLAY (REEMPLAZO SIN DUPLICADOS) ===")

    archivos = [
        f for f in os.listdir(CARPETA_SALIDA)
        if f.lower().endswith(".mp4")
        and f[0:2].isdigit()
        and not f.startswith("E")
        and not f.startswith("FIX_")
        and not f.startswith("TEMP_")
        and "_GS_" not in f      # ⬅️ NO tocar GS en FIX
    ]

    for idx, archivo in enumerate(archivos, start=1):
        inicio = time.time()

        entrada  = os.path.join(CARPETA_SALIDA, archivo)
        temporal = os.path.join(CARPETA_SALIDA, f"TEMP_{archivo}")

        log(f"[FIX] {idx:02d} — {archivo}")

        run_silencioso([
            FFMPEG, "-y",
            "-i", entrada,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-profile:v", "high",
            "-level", "4.0",
            "-x264opts", "keyint=48:min-keyint=48:no-scenecut",
            "-g", "48",
            "-bf", "2",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-ac", "2",
            "-movflags", "+faststart",
            "-map_metadata", "-1",
            "-map_chapters", "-1",
            temporal
        ])

        if not os.path.exists(temporal):
            log(f"   🟥 ERROR: FFmpeg no generó {temporal}. Se omite este archivo.")
            continue

        try:
            os.remove(entrada)
        except:
            pass

        os.rename(temporal, entrada)

        log(f"   ✔ OK ({time.time() - inicio:.2f}s)")

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("\n==============================================")
    print("MASTER PIPELINE — PLECA VERDE → PLECA ZU → BACK → GS → FIX iPLAY")
    print("==============================================\n")

    titulos = cargar_titulos()

    fase_pleca_verde(titulos)
    fase_pleca_zu(titulos)
    fase_back(titulos)
    fase_gs(titulos)

    log("Esperando 14 segundos para liberar archivos GS...")
    time.sleep(14)

    fase_fix_iplay()

    FIN = time.time()
    dur = FIN - INICIO_GLOBAL

    print("\n==============================================")
    print(f"⏱ INICIO: {datetime.fromtimestamp(INICIO_GLOBAL).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱ FIN:    {datetime.fromtimestamp(FIN).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱ DURACIÓN TOTAL: {tiempo_legible(dur)}")
    print("==============================================\n")

if __name__ == "__main__":
    main()
