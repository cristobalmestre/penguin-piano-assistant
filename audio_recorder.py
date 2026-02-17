# Stages 2 & 3: Recording the played song and summarising it into strokes.
#
# pyaudio and aubio are imported inside record_and_process() so this file
# can be imported on any machine without Pi hardware installed.

import pandas as pd
import numpy as np
from more_itertools import pairwise

from config import SONG_NAME, RECORDED_TUNES_DIR, FLAG_FILE


def record_and_process(song_name=SONG_NAME):
    """Record audio from the microphone and produce a comparison CSV.

    pyaudio and aubio are imported here so that the rest of the module
    can be imported on any machine without Pi hardware installed.
    """
    import pyaudio
    import aubio
    import time

    # Parameters for audio input
    BUFFER_SIZE = 1024
    SAMPLE_RATE = 44100
    MAX_RUNTIME = 3 * 60  # 3 minutes in seconds
    INTENSITY_THRESHOLD = 0.05  # based on actual keyboard data
    INTENSITY_RATIO_UMBRALE = 2.0  # experimental

    # Create a flag file to indicate whether processing should continue
    # Flag exists: the process keeps going
    flag_file = FLAG_FILE
    flag_file.touch()  # Create an empty flag file initially

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    pyaudio_format = pyaudio.paFloat32

    # Open a stream for microphone input
    stream = p.open(format=pyaudio_format,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=BUFFER_SIZE)

    # Initialize Aubio's pitch detection
    tolerance = 0.8
    win_s = 4096
    hop_s = BUFFER_SIZE
    pitch_o = aubio.pitch("default", win_s, hop_s, SAMPLE_RATE)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(tolerance)

    print("Listening for pitches...")

    previous_pitch = None
    start_time = time.time()
    start_time_ok = None
    elapsed_time = 0

    # Initialize an empty DataFrame to store the pitch, time, intensity, and tag data
    data_all = {'Pitch (MIDI)': [], 'Time (s)': [], 'Intensity': [], 'Tag': []}
    df_all = pd.DataFrame(data_all)

    # Initialize an empty DataFrame to store the pitch, time and intensity for only OK data
    data_ok = {'Pitch (MIDI)': [], 'Time (s)': [], 'Intensity': []}
    df_ok = pd.DataFrame(data_ok)

    try:
        while flag_file.exists():  # Check if the flag file exists

            # Read audio from the stream
            audio_data = stream.read(BUFFER_SIZE)
            samples = np.frombuffer(audio_data, dtype=np.float32)

            # Get the pitch
            pitch = pitch_o(samples)[0]

            # Calculate RMS amplitude as a measure of intensity
            intensity = np.sqrt(np.mean(samples**2))

            # Convert pitch to MIDI format
            if pitch != 0:
                midi_pitch = int(round(pitch))
                current_time = time.time()
                elapsed_time = current_time - start_time

                # Tag for cancelling noise that does not come from the keyboard
                tag = "OK" if intensity > INTENSITY_THRESHOLD else "Suspicious"

                # Add the pitch, time, intensity, and tag to the "all" DataFrame
                new_df_all = pd.DataFrame([{'Pitch (MIDI)': midi_pitch, 'Time (s)': elapsed_time, 'Intensity': intensity, 'Tag': tag}])
                df_all = pd.concat([df_all, new_df_all], axis=0, ignore_index=True)

                # Add the OK data to a separate Dataframe
                if tag == "OK":

                    if start_time_ok is None:
                        start_time_ok = elapsed_time
                        elapsed_time_ok = 0
                    else:
                        elapsed_time_ok = elapsed_time - start_time_ok

                    new_df_ok = pd.DataFrame([{'Pitch (MIDI)': midi_pitch, 'Time (s)': elapsed_time_ok, 'Intensity': intensity}])
                    df_ok = pd.concat([df_ok, new_df_ok], axis=0, ignore_index=True)

                    # Calculate time differences between rows
                    if len(df_ok) > 1:
                        time_diff = elapsed_time_ok - df_ok.iloc[-2]['Time (s)']
                        df_ok.at[len(df_ok) - 1, 'Time Diff (s)'] = time_diff

                        # Calculate intensity change (division between intensities)
                        prev_intensity = df_ok.iloc[-2]['Intensity']
                        intensity_change = intensity / prev_intensity
                        df_ok.at[len(df_ok) - 1, 'Intensity_change'] = intensity_change

                        # flag to know if the intensity change is bigger than the umbral
                        if intensity_change < INTENSITY_RATIO_UMBRALE:
                            df_ok.at[len(df_ok) - 1, 'Pitch_change_umbrale'] = 'SAME PITCH'
                        else:
                            df_ok.at[len(df_ok) - 1, 'Pitch_change_umbrale'] = 'NEW PITCH'

                    if pitch != previous_pitch:
                        print("Detected pitch (MIDI): {} with Intensity: {:.4f} - Tag: {} - at {:.2f} seconds".format(
                            midi_pitch, intensity, tag, elapsed_time))

                previous_pitch = pitch

            else:
                previous_pitch = None

            # Stop the program if three minutes have passed
            if elapsed_time >= MAX_RUNTIME:
                print("Maximum runtime reached. Stopping the program.")
                break

    except KeyboardInterrupt:
        pass

    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Stream closed.")

    # Save raw recordings
    path_recorded_songs         = RECORDED_TUNES_DIR / (song_name + '_recorded.csv')
    path_recorded_songs_w_noise = RECORDED_TUNES_DIR / (song_name + '_w_noise_recorded.csv')
    df_ok.to_csv(path_recorded_songs, index=False)
    df_all.to_csv(path_recorded_songs_w_noise, index=False)
    print("Pitch data saved to ", path_recorded_songs, " and ", path_recorded_songs_w_noise)

    # STAGE 3: Stroke summarisation
    # A summary Dataframe is needed to identify correct key strokes. This dataframe identifies
    # the Pitch-duration of each key-stroke, separating different pitches and identifying
    # repetitions. It uses intensity percent variation against previous pitches to separate sound.
    # If the buffer is not able to capture two lines of "above minimum intensity" of a stroke,
    # it is discarded as noise.

    MIN_LINES = 2
    df_strokes = df_ok

    # Create a grouper for same sequential pitches, assign a group ID and a count of lines to every group
    v = df_strokes['Pitch (MIDI)'].dropna()
    grouper = (v != v.shift()).cumsum()

    df_Group_ID = grouper.to_frame(name='Group_id')
    group_lines = df_Group_ID.groupby('Group_id').size().to_frame(name='Group_count')
    df_Group_ID = df_Group_ID.merge(group_lines, on='Group_id', how='left')

    # Remove noise: lines that do not repeat the same stroke at least MIN_LINES times are considered noise
    df_strokes = df_strokes.join(df_Group_ID, how='outer')
    df_strokes = df_strokes[df_strokes['Group_count'] >= MIN_LINES]

    # Clean cols that will no longer be required
    df_strokes = df_strokes.drop('Group_id', axis=1)
    df_strokes = df_strokes.drop('Group_count', axis=1)

    # Create a new grouper to join groups incorrectly separated by noise
    v = df_strokes['Pitch (MIDI)'].dropna()
    grouper = (v != v.shift()).cumsum()

    # Create a column that assigns different groups whenever the intensity suggests two strokes of the same pitch
    df_strokes['PITCH_Group'] = (df_strokes['Pitch_change_umbrale'] == 'NEW PITCH').cumsum()

    # Calculating the time every pitch lasts after noise cancelling
    df_strokes['Sum_times'] = df_strokes.groupby([grouper, 'PITCH_Group'])['Time Diff (s)'].cumsum()

    # Creation of a summary Dataframe to compare results against the original song
    data_summary = {
        'Pitch (MIDI)': [], 'Start Time (s)': [], 'Time difference (s)': [],
        'Max Intensity': [], 'Max Intensity change': [], 'Pitch-duration (s)': [], 'Lines recorded': []
    }
    df_strokes_summary = pd.DataFrame(data_summary)

    df_strokes_summary['Pitch (MIDI)']          = df_strokes.groupby([grouper, 'PITCH_Group'])['Pitch (MIDI)'].first()
    df_strokes_summary['Start Time (s)']         = df_strokes.groupby([grouper, 'PITCH_Group'])['Time (s)'].min()
    df_strokes_summary['Time difference (s)']    = df_strokes_summary['Start Time (s)'].diff()
    df_strokes_summary['Max Intensity']          = df_strokes.groupby([grouper, 'PITCH_Group'])['Intensity'].max()
    df_strokes_summary['Max Intensity change']   = df_strokes.groupby([grouper, 'PITCH_Group'])['Intensity_change'].max()
    df_strokes_summary['Pitch-duration (s)']     = df_strokes.groupby([grouper, 'PITCH_Group'])['Sum_times'].max()
    df_strokes_summary['Lines recorded']         = df_strokes.groupby([grouper, 'PITCH_Group'])['Pitch (MIDI)'].count()

    path_recorded_songs_for_comparison = RECORDED_TUNES_DIR / (song_name + '_for_comparison.csv')
    df_strokes_summary.to_csv(path_recorded_songs_for_comparison, index=False)
    print("Data for comparison saved to ", path_recorded_songs_for_comparison)

    return path_recorded_songs_for_comparison


if __name__ == "__main__":
    record_and_process()
