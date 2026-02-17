from pathlib import Path

# Project root - always the directory that contains this file.
# No os.chdir() needed anywhere else in the project.
BASE_DIR = Path(__file__).parent

# Song to load and compare against
SONG_NAME = 'jingle_bells easy'

# Directory paths (absolute, derived from BASE_DIR)
MIDI_FILES_DIR     = BASE_DIR / 'MIDI Files'
MIDI_CSV_DIR       = BASE_DIR / 'MIDI_to_CSV_songs'
RECORDED_TUNES_DIR = BASE_DIR / 'player_recorded_tunes'
SCREENS_DIR        = BASE_DIR / 'Screens'
INTRO_SCREENS_DIR  = SCREENS_DIR / 'Introduction_sequence'
RESULT_SCREENS_DIR = SCREENS_DIR / 'Player_reports'

# Flag file used for inter-process communication between the GUI and recorder
FLAG_FILE = BASE_DIR / 'stop_processing.flag'
