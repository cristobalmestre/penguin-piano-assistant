# Stage 1: Reading and parsing a MIDI file.
# No hardware dependency - can be imported and tested on any machine.

import pandas as pd
import pretty_midi

from config import SONG_NAME, MIDI_FILES_DIR, MIDI_CSV_DIR


def parse_midi(song_name=SONG_NAME):
    """Parse the reference MIDI file and write it as a CSV for later comparison."""

    song_to_midi = MIDI_FILES_DIR / (song_name + '.mid')
    midi_data = pretty_midi.PrettyMIDI(str(song_to_midi))

    tiempo = midi_data.get_end_time()
    print('time: ', tiempo, ' seconds')

    # Total piano strokes
    Note_sequence = midi_data.instruments[0].notes

    note_pitches = []
    note_start_times = []
    note_end_times = []
    note_velocities = []

    for note in Note_sequence:
        note_pitches.append(note.pitch)
        note_start_times.append(note.start)
        note_end_times.append(note.end)
        note_velocities.append(note.velocity)

    # Create a pandas Dataframe with the notes and their characteristics
    dataset = pd.DataFrame(
        {'pitches': note_pitches, 'start': note_start_times, 'end': note_start_times, 'velocity': note_velocities},
        columns=['pitches', 'start', 'end', 'velocity']
    )
    dataset = dataset.sort_values(by=['start'], ascending=True)
    dataset['start_diff'] = dataset['start'].diff()

    # Save the DataFrame to a CSV file
    path_original_song = MIDI_CSV_DIR / (song_name + '.csv')
    dataset.to_csv(path_original_song, index=False)
    print("Original song saved to ", path_original_song)

    return path_original_song


if __name__ == "__main__":
    parse_midi()
