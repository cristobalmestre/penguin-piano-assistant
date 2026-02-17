# -*- coding: utf-8 -*-
"""
test_config.py - Offline test suite for the Piano Assistant.

Run this on any machine (Windows, Mac, Linux) to verify that:
  1. config.py resolves all paths correctly from wherever the project lives.
  2. Required directories exist (or can be created).
  3. The MIDI file can be parsed and its CSV output written.
  4. The scoring algorithm can read its input files and return valid results.
  5. All non-hardware modules can be imported without errors.

Hardware-dependent modules (digitalio, board, adafruit_rgb_display, pyaudio,
aubio) are skipped automatically with a clear SKIP message.

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

# --- 1. config.py -------------------------------------------------------------
print("\n-- 1. config.py paths --------------------------------------------------")

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

# --- 2. MIDI file exists ------------------------------------------------------
print("\n-- 2. Reference MIDI file ----------------------------------------------")

midi_path = MIDI_FILES_DIR / (SONG_NAME + ".mid")
check("'%s.mid' found in MIDI Files/" % SONG_NAME,
      lambda: None if midi_path.exists() else (_ for _ in ()).throw(FileNotFoundError(midi_path)))

# --- 3. MIDI parsing -> CSV ---------------------------------------------------
print("\n-- 3. MIDI parsing (pretty_midi + pandas) ------------------------------")

try:
    import pretty_midi
    import pandas as pd

    def _parse_midi():
        midi_data = pretty_midi.PrettyMIDI(str(midi_path))
        notes = midi_data.instruments[0].notes
        pitches    = [n.pitch    for n in notes]
        starts     = [n.start    for n in notes]
        ends       = [n.end      for n in notes]
        velocities = [n.velocity for n in notes]
        df = pd.DataFrame({
            "pitches": pitches, "start": starts, "end": ends, "velocity": velocities
        })
        df = df.sort_values("start")
        df["start_diff"] = df["start"].diff()
        out_path = MIDI_CSV_DIR / (SONG_NAME + ".csv")
        df.to_csv(out_path, index=False)
        return "%d notes written to %s" % (len(notes), out_path.name)

    check("Parse MIDI and write reference CSV", _parse_midi)

except ImportError as e:
    skip("MIDI parsing", "library not installed (%s) - install with: pip install pretty_midi pandas" % e)

# --- 4. Scoring algorithm -----------------------------------------------------
print("\n-- 4. Scoring algorithm (Comparison_scoring.py) ------------------------")

ref_csv  = MIDI_CSV_DIR       / (SONG_NAME + ".csv")
play_csv = RECORDED_TUNES_DIR / (SONG_NAME + "_for_comparison.csv")

if not ref_csv.exists():
    skip("calculate_scores()", "reference CSV not generated (MIDI parsing step failed/skipped)")
elif not play_csv.exists():
    skip("calculate_scores()",
         "no recorded comparison file found.\n"
         "         Expected: %s\n"
         "         Copy a sample '*_for_comparison.csv' there to test scoring." % play_csv)
else:
    try:
        import Comparison_scoring
        def _run_scoring():
            p_score, p_cat, t_score, t_cat = Comparison_scoring.calculate_scores()
            return "pitch=%.1f (%s), time=%.1f (%s)" % (p_score, p_cat, t_score, t_cat)
        check("calculate_scores() returns valid results", _run_scoring)
    except Exception as e:
        print("  %s  calculate_scores(): %s" % (FAIL, e))
        results.append(("fail", "calculate_scores()"))

# --- 5. Module import checks --------------------------------------------------
print("\n-- 5. Module imports ---------------------------------------------------")

HARDWARE_MODULES = {"digitalio", "board", "adafruit_rgb_display",
                    "adafruit_blinka", "pyaudio", "aubio"}

modules_to_check = [
    ("config_assistant",     "setup / directory creation"),
    ("Comparison_scoring",   "scoring algorithm"),
    ("pretty_midi",          "MIDI parsing"),
    ("pandas",               "data processing"),
    ("numpy",                "numerical ops"),
    ("PIL",                  "image handling (Pillow)"),
    ("more_itertools",       "pairwise utility"),
    ("tkinter",              "GUI toolkit"),
    ("pyaudio",              "audio recording"),
    ("aubio",                "pitch detection"),
    ("digitalio",            "Pi GPIO (hardware)"),
    ("board",                "Pi board pins (hardware)"),
    ("adafruit_rgb_display", "Pi display driver (hardware)"),
]

for mod, desc in modules_to_check:
    top = mod.split(".")[0]
    if top in HARDWARE_MODULES:
        try:
            importlib.import_module(mod)
            print("  %s  %-30s (%s)" % (PASS, mod, desc))
            results.append(("pass", "import " + mod))
        except ImportError:
            skip("import %s (%s)" % (mod, desc), "Pi hardware - expected on Windows/Mac")
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
print("  %d passed  |  %d failed  |  %d skipped (hardware)\n" % (passed, failed, skipped))

if failed:
    print("  Failed checks:")
    for r in results:
        if r[0] == "fail":
            print("    - " + r[1])
    sys.exit(1)
else:
    print("  All testable checks passed. Safe to deploy to the Pi.")
