# broadcast-natron-automatitation
# Broadcast Pipeline Automation*  An automated, data-driven post-production pipeline designed for TV networks, newsrooms, and digital media agencies. Powered by **Python**, **Natron (VFX Architecture)**, and **FFmpeg**.
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 The Core Issue
In the day-to-day operations of a TV station or news portal, reporters and editors generate dozens of raw stories (VO, SOT, FT, Splits). The real bottleneck begins when an editor has to manually apply the **show's visual identity**: placing lower-thirds without typos, rendering background screens (Greenscreens), unifying the branding, and processing specific broadcast delivery formats (such as iPlay). 

This repetitive process consumes between **2 to 4 hours daily per editor**—valuable time that should instead be spent on improving the visual narrative and the core assembly of the story.

## 💡 The Revolutionary Solution
This project completely automates graphical identity injection and broadcast video formatting en masse, driven entirely by data from an Excel rundown.

The manual workflow is reduced to just 3 steps for the user:
1. The producer or assistant fills out the day's rundown in an **Excel** file.
2. Raw assets are placed in their respective folders.
3. The pipeline is executed. The script handles headless visual effects rendering in Natron and ultra-fast packaging via FFmpeg.

**The Result:** No more typos in anchors' names, guaranteed homogeneous branding on every frame, and files ready for the playout server in minutes.

---

## ⚙️ Key Features

* **Data-Driven Graphics:** Automated import of titles and metadata from traditional production rundowns (Excel/Openpyxl).
* **Headless Visual Effects:** Background automation of templates composited via **Natron Renderer** (Greenscreen compositing and dynamic motion graphics).
* **Smart Remuxing:** Frame-accurate merging of the stories' original audio without sync loss, using optimized **FFmpeg** commands.
* **Broadcast-Safe Formatting:** An automated phase to ensure compliance with the iPLAY standard and TV playout servers (H.264, 48kHz audio, YUV420p, closed GOP for commercial break insertion).
* **Express Rundown Cutter:** Includes an auxiliary module to fragment long, full-program recordings into independent stories in less than 10 seconds without any quality loss (`-c copy`).

---

## 🛠️ Pipeline Architecture

The system operates through 5 critical automation phases:

1. **Phase 1 (Green Lower-Third):** Automated rendering of clean text elements over an alpha channel.
2. **Phase 2 (Zu Lower-Third):** Generation of template-driven animated graphics for strict duration control.
3. **Phase 3 (Back / Blur):** Dynamic duration analysis via `ffprobe`, generation of Gaussian blur backgrounds, and remuxing of the original audio.
4. **Phase 4 (Greenscreen):** Background injection of B-roll images and dynamic titles into automated typographic environments.
5. **Phase 5 (Fix iPlay):** Final atomic transcoding using rigorous transmission parameters (optimized GOP and keyframes for master playout servers).

---

## 📂 Project Structure

```text
├── Base/
│   ├── mov/                # Base animated branding assets (Backlogos, etc.)
│   └── BackBlur-720.png    # Optimized buffer pre-renders
├── Materiales/
│   ├── Imagenes/           # Daily B-roll images (gs01.jpg, gs02.jpg...)
│   ├── Videos/             # Raw videos or completed stories (nota01.mp4...)
│   └── RFPauta-diaria.xlsx # Commercial/editorial rundown in Excel
├── NatronPlantillas/       # Modular composition files (.ntp)
├── master_pipeline.py      # Core executable for the full workflow
└── cortador_pauta.py       # Auxiliary script for timecode-based cutting
