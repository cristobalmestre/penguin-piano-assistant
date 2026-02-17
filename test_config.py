# -*- coding: utf-8 -*-
"""
test_config.py - Offline test suite for the Piano Assistant.

Tests every file that can be tested without Pi hardware by importing and
calling the real functions directly. Nothing is reimplemented here.

FILES TESTED (real imports, real function calls):
  - config.py                  All path constants verified
  - config_assistant.py        Import check (no crash, directories created)
  - Read_MIDI_record_compare.py  parse_midi() called for real (no hardware needed)
  - Comparison_scoring.py      calculate_scores() called for real
  - graphic_interphase_for_pi.py  Import check, App class structure verified

WHAT CANNOT BE TESTED ON WINDOWS (hardware required):
  - record_and_process() in Read_MIDI_record_compare.py
        Needs pyaudio + aubio + microphone (Pi only)
  - App.__init__() in graphic_interphase_for_pi.py
        Needs digitalio + board + adafruit display (Pi only)
  - The full GUI flow
        Same reason as above

Usage:
    python test_config.py
"""

import sys

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

# --- 2. config_assistant.py (real import) -------------------------------------
print("\n-- 2. config_assistant.py (real import) --------------------------------")

try:
    import config_assistant
    check("config_assistant imports without crashing", lambda: None)
    check("create_directories() runs without error",
          lambda: config_assistant.create_directories(config_assistant.directories))
except ImportError as e:
    print("  %s  import config_assistant: %s" % (FAIL, e))
    results.append(("fail", "import config_assistant"))

# --- 3. Read_MIDI_record_compare.py - parse_midi() (real function) ------------
print("\n-- 3. Read_MIDI_record_compare.py - parse_midi() (real function) -------")

try:
    import Read_MIDI_record_compare

    check("Module imports without crashing (no hardware triggered)", lambda: None)

    midi_path = MIDI_FILES_DIR / (SONG_NAME + ".mid")
    if not midi_path.exists():
        skip("parse_midi()", "'%s.mid' not found in MIDI Files/" % SONG_NAME)
    else:
        def _run_parse_midi():
            out_path = Read_MIDI_record_compare.parse_midi(SONG_NAME)
            import pandas as pd
            df = pd.read_csv(out_path)
            return "%d notes parsed and saved to %s" % (len(df), out_path.name)
        check("parse_midi() parses MIDI and writes reference CSV", _run_parse_midi)

    skip("record_and_process()",
         "needs pyaudio + aubio + microphone - Pi hardware only")

except ImportError as e:
    print("  %s  import Read_MIDI_record_compare: %s" % (FAIL, e))
    results.append(("fail", "import Read_MIDI_record_compare"))

# --- 4. Comparison_scoring.py - calculate_scores() (real function) ------------
print("\n-- 4. Comparison_scoring.py - calculate_scores() (real function) -------")

ref_csv  = MIDI_CSV_DIR       / (SONG_NAME + ".csv")
play_csv = RECORDED_TUNES_DIR / (SONG_NAME + "_for_comparison.csv")

if not ref_csv.exists():
    skip("calculate_scores()",
         "No reference CSV found - run parse_midi() first (section 3 above)")
elif not play_csv.exists():
    skip("calculate_scores()",
         "No recorded comparison file found at:\n"
         "         %s\n"
         "         Run the program on the Pi to generate it, then copy it here." % play_csv)
else:
    try:
        import Comparison_scoring
        check("Comparison_scoring imports without crashing", lambda: None)
        def _run_scoring():
            p_score, p_cat, t_score, t_cat = Comparison_scoring.calculate_scores()
            return "pitch=%.1f (%s), time=%.1f (%s)" % (p_score, p_cat, t_score, t_cat)
        check("calculate_scores() runs and returns valid results", _run_scoring)
    except Exception as e:
        print("  %s  calculate_scores(): %s" % (FAIL, e))
        results.append(("fail", "calculate_scores()"))

# --- 5. graphic_interphase_for_pi.py (real import, class structure) -----------
print("\n-- 5. graphic_interphase_for_pi.py (real import) -----------------------")

try:
    import graphic_interphase_for_pi

    check("Module imports without crashing (hardware imports deferred to __init__)",
          lambda: None)
    check("App class exists in the module",
          lambda: None if hasattr(graphic_interphase_for_pi, 'App') else
                  (_ for _ in ()).throw(AttributeError("App class not found")))
    check("App.next_stage method exists",
          lambda: None if hasattr(graphic_interphase_for_pi.App, 'next_stage') else
                  (_ for _ in ()).throw(AttributeError("next_stage not found")))
    check("App.execute_compare method exists",
          lambda: None if hasattr(graphic_interphase_for_pi.App, 'execute_compare') else
                  (_ for _ in ()).throw(AttributeError("execute_compare not found")))
    check("App.show_image method exists",
          lambda: None if hasattr(graphic_interphase_for_pi.App, 'show_image') else
                  (_ for _ in ()).throw(AttributeError("show_image not found")))

    skip("App() instantiation",
         "App.__init__ connects to Pi display hardware - Pi only")

except ImportError as e:
    print("  %s  import graphic_interphase_for_pi: %s" % (FAIL, e))
    results.append(("fail", "import graphic_interphase_for_pi"))

# --- Summary ------------------------------------------------------------------
print("\n-- Summary -------------------------------------------------------------")
passed  = sum(1 for r in results if r[0] == "pass")
failed  = sum(1 for r in results if r[0] == "fail")
skipped = sum(1 for r in results if r[0] == "skip")
print("  %d passed  |  %d failed  |  %d skipped\n" % (passed, failed, skipped))

if skipped:
    print("  Skipped (Pi hardware required):")
    for r in results:
        if r[0] == "skip":
            print("    - " + r[1])
    print()

if failed:
    print("  FAILED checks:")
    for r in results:
        if r[0] == "fail":
            print("    - " + r[1])
    sys.exit(1)
else:
    print("  All testable checks passed.")
    print("  To fully test, deploy to the Pi and verify recording and display.")
