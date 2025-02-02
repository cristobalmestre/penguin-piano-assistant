# STAGE 1: Reading and parsing a MIDI file to understand music in it

# Basic libraries for managing information and folders

import pandas as pd 
import numpy as np
# from itertools import pairwise
from more_itertools import pairwise
import os


# importing pretty_midi library for procesing MIDI files
import pretty_midi

# Load MIDI file into PrettyMIDI object

# Gather name of the song
from config_assistant import song_name
#song_name = 'jingle_bells easy'

# Open song
song_to_midi = 'MIDI Files/'+song_name+'.mid'
midi_data = pretty_midi.PrettyMIDI(song_to_midi)

# TEST: Print an empirical estimate of its global tempo
#print (midi_data.estimate_tempo())

tiempo = midi_data.get_end_time()
print('time: ',tiempo,' seconds')

# Total piano strokes
Note_sequence = midi_data.instruments[0].notes
#Note_sequence

# print(f'Total piano strokes: {len(Note_sequence)}')


# Testing the "note" object
# Note_sequence[0].pitch

# Create a pandas Dataframe to sort the music notes and the times between each key stroke

note_pitches = []
note_start_times = []
note_end_times = []
note_velocities = []


for note in Note_sequence:
    note_pitches.append(note.pitch)
    note_start_times.append(note.start)
    note_end_times.append(note.end)
    note_velocities.append(note.velocity)


# create a pandas Dataframe with the notes and their characteristics
dataset = pd.DataFrame({'pitches': note_pitches, 'start': note_start_times, 'end': note_start_times, 'velocity': note_velocities } ,columns=['pitches', 'start', 'end', 'velocity'])
dataset = dataset.sort_values(by=['start'], ascending=True)
dataset['start_diff']= dataset['start'].diff()

# Save the DataFrame to a CSV file

# create the file name on the correct folder
song_name_csv = song_name+'.csv'
base_dir = r'MIDI_to_CSV_songs'
path_original_song = os.path.join(base_dir, song_name_csv)

# saving the CSV file
dataset.to_csv(path_original_song, index=False)
print("Original song saved to ",path_original_song)

# Test the dataset
#dataset

# Coding to interpret MIDI Files ends here. Next stage: recording and managing sound.

# STAGE 2: Recording and interpreting the played song

import pyaudio
import aubio
import time


# Parameters for audio input
BUFFER_SIZE = 1024
SAMPLE_RATE = 44100
MAX_RUNTIME = 3 * 60  # 3 minutes in seconds
INTENSITY_THRESHOLD = 0.05  # based on actual keyboard data
INTENSITY_RATIO_UMBRALE = 2.0 # experimental

# Create a flag file to indicate whether processing should continue
# Flag exists: the process keeps going
flag_file = "stop_processing.flag"
open(flag_file, 'w').close()  # Create an empty flag file initially

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
    while os.path.exists(flag_file):  # Check if the flag file exists

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
                    
                    # flag to know the if the intensity change is bigger that the umbral
                    if intensity_change < INTENSITY_RATIO_UMBRALE:
                        df_ok.at[len(df_ok) - 1, 'Pitch_change_umbrale'] = 'SAME PITCH'
                    else:
                        df_ok.at[len(df_ok) - 1, 'Pitch_change_umbrale'] = 'NEW PITCH'
                
                                
                # TEST lines for OK pitches
                if pitch != previous_pitch:
                    #print(f'Detected pitch (MIDI): {midi_pitch} with Intensity: {intensity:.4f} - Tag: {tag} - at {elapsed_time:.2f} seconds')
                    print("Detected pitch (MIDI): {} with Intensity: {:.4f} - Tag: {} - at {:.2f} seconds".format(midi_pitch, intensity, tag, elapsed_time))
                
            # TEST lines to understand that we are recording Works for all pitches
            #if pitch != previous_pitch:
            #    print(f"Detected pitch (MIDI): {midi_pitch} with Intensity: {intensity:.4f} - Tag: {tag} - at {elapsed_time:.2f} seconds")

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


# create the file names on the correct folder. 2 versions are created: one with all the input and one with the pitches that meet the minimum intensity
song_name_csv = song_name+'_recorded.csv'
song_name_csv_w_noise = song_name+'_w_noise_recorded.csv'
base_dir = r'player_recorded_tunes'

path_recorded_songs = os.path.join(base_dir, song_name_csv)
path_recorded_songs_w_noise = os.path.join(base_dir, song_name_csv_w_noise)

# saving the DataFrame to a CSV file
df_ok.to_csv(path_recorded_songs, index=False)
df_all.to_csv(path_recorded_songs_w_noise, index=False)


print("Pitch data saved to ",path_recorded_songs," and ",path_recorded_songs_w_noise)

# A summary Dataframe is needed to identify correct key strokes. This dataframe identifies the Pitch-duration of each key-stroke, separating diferent
# pitches and identifying repetitions. It uses intensity percent variation against previous pitches to separate sound.
# if the buffer is ot able to capture two lines of "above minimum intensity" of a stroke, it is discarded as noise.

MIN_LINES = 2
df_strokes = df_ok

# Create a grouper for same sequential pitches, assing a group ID and a count of lines to every group of pitches.
v = df_strokes['Pitch (MIDI)'].dropna()
grouper = (v!=v.shift()).cumsum()
#grouper

df_Group_ID = grouper.to_frame(name = 'Group_id')
group_lines = df_Group_ID.groupby('Group_id').size().to_frame(name = 'Group_count')
df_Group_ID = df_Group_ID.merge(group_lines, on='Group_id', how='left')

# TEST
#df_Group_ID

# remove noise: lines that do not repeat the same stroke at least "MIN_LINES" times are considered noise
df_strokes = df_strokes.join(df_Group_ID, how='outer')
df_strokes = df_strokes[df_strokes['Group_count'] >= MIN_LINES]

# TEST
#df_strokes

# Clean cols that will no longer be requiered
df_strokes = df_strokes.drop('Group_id', axis=1)
df_strokes = df_strokes.drop('Group_count', axis=1)


# Create a new grouper to join groups incorrectly separated by noise
v = df_strokes['Pitch (MIDI)'].dropna()
grouper = (v!=v.shift()).cumsum()
#grouper

# Create a column that assign different groups whenever the intensity suggest there are two stokes of the same pitch
df_strokes['PITCH_Group'] = (df_strokes['Pitch_change_umbrale'] == 'NEW PITCH').cumsum()

# Calculating the time every pitch lasts after noise cancelling
df_strokes['Sum_times'] = df_strokes.groupby([grouper,'PITCH_Group'])['Time Diff (s)'].cumsum()

# Creation of a summary Dataframe to compare results against the original song.
# This Dataframe has been cleared from noise and multiple pitch registers (unless there are actually more than one in a row)

data_summary = {'Pitch (MIDI)': [], 'Start Time (s)': [], 'Time difference (s)': [], 'Max Intensity': [],'Max Intensity change': [], 'Pitch-duration (s)': [], 'Lines recorded': []}
df_strokes_summary = pd.DataFrame(data_summary)

df_strokes_summary['Pitch (MIDI)'] = df_strokes.groupby([grouper,'PITCH_Group'])['Pitch (MIDI)'].first()
df_strokes_summary['Start Time (s)'] = df_strokes.groupby([grouper,'PITCH_Group'])['Time (s)'].min()
df_strokes_summary['Time difference (s)'] = df_strokes_summary['Start Time (s)'].diff()
df_strokes_summary['Max Intensity'] = df_strokes.groupby([grouper,'PITCH_Group'])['Intensity'].max()
df_strokes_summary['Max Intensity change'] = df_strokes.groupby([grouper,'PITCH_Group'])['Intensity_change'].max()
df_strokes_summary['Pitch-duration (s)'] = df_strokes.groupby([grouper,'PITCH_Group'])['Sum_times'].max()
df_strokes_summary['Lines recorded'] = df_strokes.groupby([grouper,'PITCH_Group'])['Pitch (MIDI)'].count()


song_name_csv_for_comparison = song_name+'_for_comparison.csv'
path_recorded_songs_for_comparison = os.path.join(base_dir, song_name_csv_for_comparison)
df_strokes_summary.to_csv(path_recorded_songs_for_comparison, index=False)

print("Data for comparison saved to ",path_recorded_songs_for_comparison)

# TEST: dataframe that holds the pitches recorded by the user.
#df_strokes_summary

# End of recording and interpreting the played tune. Next step is to compare the original song against the played tune.
