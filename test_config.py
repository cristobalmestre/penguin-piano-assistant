# -*- coding: utf-8 -*-
"""
test_config.py - Offline test suite for the Piano Assistant.

This script tests what it can genuinely test on Windows/Mac without Pi hardware.
It is honest about what it cannot test and why.

FILES TESTED HERE (directly, using real code):
  - config.py               All path constants
  - config_assistant.py     Module import (no crash on import)
  - Comparison_scoring.py   calculate_scores() called for real

FILES THAT CANNOT BE TESTED ON WINDOWS (hardware required):
  - Read_MIDI_record_compare.py
        Reason: imports pyaudio and opens a microphone stream at the top level
        the instant it is imported. Cannot be imported without Pi hardware.
  - graphic_interphase_for_pi.py
        Reason: imports digitalio, board, adafruit_rgb_display at the top level.
        Cannot be imported without Pi GPIO hardware.

These two files are tested only by running the full program on the Pi.

Usage:
    python test_config.py
"""

import sys
import importlib

PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"
INFO = "[INFO]"

results = []

def check(label, fn):
    try:
        msg = fn()
        print("  %s  %s%s" % (PASS, label, (": " + str(msg)) if msg else ""))
        results.append(("pass", label))
    except Exception as e:
        print("  %s  %s: %s" % (FAIL, label, e))
        results.append(("fail", label))

def skip(label, reason):
    print("  %s  %s: %s" % (SKIP, label, reason))
    results.append(("skip", label))

# --- 1. config.py (real file) -------------------------------------------------
print("\n-- 1. config.py paths (testing the real config.py) --------------------")

try:
    from config import (BASE_DIR, SONG_NAME, MIDI_FILES_DIR, MIDI_CSV_DIR,
                        RECORDED_TUNES_DIR, SCREENS_DIR, INTRO_SCREENS_DIR,
                        RESULT_SCREENS_DIR, FLAG_FILE)
    print("  %s  BASE_DIR = %s" % (INFO, BASE_DIR))

    check("BASE_DIR points to an existing directory",
          lambda: None if BASE_DIR.is_dir() else (_ for _ in ()).throw(FileNotFoundError(BASE_DIR)))
    check("SONG_NAME is a non-empty string",
          lambda: repr(SONG_NAME) if SONG_NAME else (_ for _ in ()).throw(ValueError("empty")))
    check("MIDI_FILES_DIR exists",
          lambda: None if MIDI_FILES_DIR.is_dir() else (_ for _ in ()).throw(FileNotFoundError(MIDI_FILES_DIR)))
    check("MIDI_CSV_DIR exists (or can be created)",
          lambda: MIDI_CSV_DIR.mkdir(parents=True, exist_ok=True))
    check("RECORDED_TUNES_DIR exists (or can be created)",
          lambda: RECORDED_TUNES_DIR.mkdir(parents=True, exist_ok=True))
    check("SCREENS_DIR exists",
          lambda: None if SCREENS_DIR.is_dir() else (_ for _ in ()).throw(FileNotFoundError(SCREENS_DIR)))
    check("INTRO_SCREENS_DIR exists",
          lambda: None if INTRO_SCREENS_DIR.is_dir() else (_ for _ in ()).throw(FileNotFoundError(INTRO_SCREENS_DIR)))
    check("RESULT_SCREENS_DIR exists",
          lambda: None if RESULT_SCREENS_DIR.is_dir() else (_ for _ in ()).throw(FileNotFoundError(RESULT_SCREENS_DIR)))
    check("FLAG_FILE path is inside BASE_DIR",
          lambda: None if FLAG_FILE.parent == BASE_DIR else (_ for _ in ()).throw(ValueError(FLAG_FILE)))

except ImportError as e:
    print("  %s  Could not import config.py: %s" % (FAIL, e))
    sys.exit(1)

# --- 2. Reference MIDI file ---------------------------------------------------
print("\n-- 2. Reference MIDI file ----------------------------------------------")

midi_path = MIDI_FILES_DIR / (SONG_NAME + ".mid")
check("'%s.mid' found in MIDI Files/" % SONG_NAME,
      lambda: None if midi_path.exists() else (_ for _ in ()).throw(FileNotFoundError(midi_path)))

# --- 3. Read_MIDI_record_compare.py (CANNOT test on Windows) ------------------
print("\n-- 3. Read_MIDI_record_compare.py --------------------------------------")
print("  %s  This file cannot be imported on Windows." % SKIP)
print("       It calls pyaudio.PyAudio() and opens a microphone stream at the")
print("       top level, which requires Pi hardware. Test this on the Pi only.")
results.append(("skip", "Read_MIDI_record_compare.py"))

# --- 4. Comparison_scoring.py (real function, real file) ----------------------
print("\n-- 4. Comparison_scoring.py - calculate_scores() (real function) -------")

ref_csv  = MIDI_CSV_DIR       / (SONG_NAME + ".csv")
play_csv = RECORDED_TUNES_DIR / (SONG_NAME + "_for_comparison.csv")

if not ref_csv.exists():
    skip("calculate_scores()",
         "No reference CSV found at: %s\n"
         "         Run the program once on the Pi to generate it, then copy it here." % ref_csv)
elif not play_csv.exists():
    skip("calculate_scores()",
         "No recorded comparison file found at:\n"
         "         %s\n"
         "         Run the program once on the Pi to generate it, then copy it here." % play_csv)
else:
    try:
        import Comparison_scoring
        def _run_scoring():
            p_score, p_cat, t_score, t_cat = Comparison_scoring.calculate_scores()
            return "pitch=%.1f (%s), time=%.1f (%s)" % (p_score, p_cat, t_score, t_cat)
        check("calculate_scores() runs and returns valid results", _run_scoring)
    except Exception as e:
        print("  %s  calculate_scores(): %s" % (FAIL, e))
        results.append(("fail", "calculate_scores()"))

# --- 5. graphic_interphase_for_pi.py (CANNOT test on Windows) -----------------
print("\n-- 5. graphic_interphase_for_pi.py ------------------------------------")
print("  %s  This file cannot be imported on Windows." % SKIP)
print("       It imports digitalio, board, and adafruit_rgb_display at the top")
print("       level, which require Pi GPIO hardware. Test this on the Pi only.")
results.append(("skip", "graphic_interphase_for_pi.py"))

# --- 6. Module imports --------------------------------------------------------
print("\n-- 6. Python package availability -------------------------------------")

HARDWARE_MODULES = {"digitalio", "board", "adafruit_rgb_display",
                    "adafruit_blinka", "pyaudio", "aubio"}

modules_to_check = [
    ("config_assistant",     "setup script  (real file import)"),
    ("Comparison_scoring",   "scoring logic (real file import)"),
    ("pretty_midi",          "MIDI parsing"),
    ("pandas",               "data processing"),
    ("numpy",                "numerical ops"),
    ("PIL",                  "image handling (Pillow)"),
    ("more_itertools",       "pairwise utility"),
    ("tkinter",              "GUI toolkit"),
    ("pyaudio",              "audio recording     [Pi hardware]"),
    ("aubio",                "pitch detection     [Pi hardware]"),
    ("digitalio",            "Pi GPIO             [Pi hardware]"),
    ("board",                "Pi board pins       [Pi hardware]"),
    ("adafruit_rgb_display", "Pi display driver   [Pi hardware]"),
]

for mod, desc in modules_to_check:
    top = mod.split(".")[0]
    if top in HARDWARE_MODULES:
        try:
            importlib.import_module(mod)
            print("  %s  %-30s (%s)" % (PASS, mod, desc))
            results.append(("pass", "import " + mod))
        except ImportError:
            skip("import %s" % mod, desc + " - not available on Windows, expected")
    else:
        try:
            importlib.import_module(mod)
            print("  %s  %-30s (%s)" % (PASS, mod, desc))
            results.append(("pass", "import " + mod))
        except ImportError as e:
            print("  %s  %-30s (%s): %s" % (FAIL, mod, desc, e))
            results.append(("fail", "import " + mod))

# --- Summary ------------------------------------------------------------------
print("\n-- Summary -------------------------------------------------------------")
passed  = sum(1 for r in results if r[0] == "pass")
failed  = sum(1 for r in results if r[0] == "fail")
skipped = sum(1 for r in results if r[0] == "skip")
print("  %d passed  |  %d failed  |  %d skipped\n" % (passed, failed, skipped))

print("  What is skipped and why:")
print("  - Read_MIDI_record_compare.py : opens microphone on import (needs pyaudio + Pi)")
print("  - graphic_interphase_for_pi.py: imports GPIO libs on import (needs Pi)")
print("  - Pi hardware packages        : not available on Windows")
print()

if failed:
    print("  FAILED checks:")
    for r in results:
        if r[0] == "fail":
            print("    - " + r[1])
    sys.exit(1)
else:
    print("  All testable checks passed.")
    print("  To fully test, run the program on the Pi and verify the display and recording work.")
