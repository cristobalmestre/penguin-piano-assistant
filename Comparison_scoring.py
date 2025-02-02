# STAGE 3: Comparison and scoring algorithim

import pandas as pd 
import numpy as np
# from itertools import pairwise
from more_itertools import pairwise
import os

# read the original song in CSV 
#def calculate_scores(result_queue):
def calculate_scores():

    print("Opening the csv register of the original song")
    from config_assistant import song_name
    #song_name = 'jingle_bells easy'
    song_name_csv = song_name+'.csv'
    base_dir = r'MIDI_to_CSV_songs'
    path_original_song = os.path.join(base_dir, song_name_csv)

    correct_song = pd.read_csv(path_original_song)
    print("Original song succesfully retrieved")

    # Test the Dataframe
    #correct_song


    # read the transcription for comparison in CSV 

    print("Opening Transcription of the played song (for comparison)")
    recorded_song_name_csv = song_name+'_for_comparison.csv'
    recorded_base_dir = r'player_recorded_tunes'
    path_recorded_songs = os.path.join(recorded_base_dir, recorded_song_name_csv)


    # Testing with file containing the real song comparison (NEED TO EDIT)
    #path_recorded_songs = os.path.join(recorded_base_dir, 'jingle_bells easy_recorded - real.csv')
    recorded_song = pd.read_csv(path_recorded_songs)


    # IMPORTANT: Remember to replace for the real file after tests!!!
    recorded_song = pd.read_csv(path_recorded_songs)
    print("Trasncription succesfully retrieved")

    # Test the Dataframe
    # recorded_song

    # Create an "original pitches" vector, that will be used to assess the correctness of the player
    original_pitches = correct_song['pitches'].to_numpy()
    print('There are ',original_pitches.size,' pitches in the song')

    #original_pitches

    # Create a "played pitches" vector, that will be compared agaist the "original pitches"
    played_pitches = recorded_song['Pitch (MIDI)'].to_numpy()
    print('And they will be compared to ',played_pitches.size,' pitches in the played song')

    #played_pitches

    # Create an "original pitches time difference" vector, that will be used to assess the correctness of the player
    original_pitches_timediff = correct_song['start_diff'].to_numpy()
    print('There are ',original_pitches_timediff.size,' time-differences in the song')

    #original_pitches_timediff

    # Create a "played pitches time difference" vector, that will be compared agaist the "original pitches"
    played_pitches_timediffs = recorded_song['Time difference (s)'].to_numpy()
    print('And they will be compared to ',played_pitches_timediffs.size,' time-differences in the played song')

    #played_pitches_timediffs


    # PITCH COMPARISON ALGORITHM RULES
    # define pitch score based on stoke accuracy. the score will translate to a percentaje based on the played pitches
    # perfect match gives 100 points. Approximate match (next or previous pitch) gives 80 points.
    # matching system considers that the user can repeat, skip a pitch or go back one position if mistakes are made

    # TEMPO COMPARISON ALGORITHM RULES
    # Evaluate the correct vector: only correct pitches' time differences are compared. The time comparison is between them and the previous pitch 
    # (whether correct of not).
    # Based on this criteria, 2 new time_diff vectors will be created: one for original reproduction, another for played reproduction.
    # Vectors will be normalized to asess tempo consistency over strict time coincidence.

    perfect_pitch_val = 100
    ok_pitch_val = 80

    pitch_score = 0
    eval_vector = [] 
    
        
    # Create vectors for time differences that will be used in the time scoring system, values and umbrals for the scoring system

    original_time_diff_considered = []
    played_time_diff_considered = []
    index_register = []
    played_index_register = []

    perfect_time_val = 100
    ok_time_val = 80

    perfect_time_umbral = 0.1
    ok_time_umbral = 0.5

    # Define a cursor that will navigate through the original song pitches 
    original_cursor = 0

    for played_cursor in range(played_pitches.size):
        
        # print(played_cursor)
        
        if played_cursor == 0:
        
            if played_pitches[played_cursor] == original_pitches[original_cursor]:

                pitch_score +=perfect_pitch_val
                eval_vector.append('Corr')
                original_cursor +=1
                

            elif played_pitches[played_cursor] == original_pitches[original_cursor +1]:
                
                pitch_score +=ok_pitch_val
                eval_vector.append('n+1')
                original_cursor +=2
                
            else:
                eval_vector.append('Incor')
                original_cursor +=1
                
                
        elif played_cursor == 1:
            
            if played_pitches[played_cursor] == original_pitches[original_cursor]:

                pitch_score +=perfect_pitch_val
                eval_vector.append('Corr')
                original_time_diff_considered.append(original_pitches_timediff[original_cursor])
                played_time_diff_considered.append(played_pitches_timediffs[played_cursor])
                index_register.append(original_cursor)
                played_index_register.append(played_cursor)
                original_cursor +=1
                

            elif played_pitches[played_cursor] == original_pitches[original_cursor +1]:
                
                pitch_score +=ok_pitch_val
                eval_vector.append('n+1')
                original_cursor +=2
                
            elif played_pitches[played_cursor] == original_pitches[original_cursor -1]:
                
                pitch_score +=ok_pitch_val
                eval_vector.append('n-1')
                original_cursor +=0
                
            else:
                eval_vector.append('Incor')
                original_cursor +=1
                
        else:
            
            if played_pitches[played_cursor] == original_pitches[original_cursor]:

                pitch_score +=perfect_pitch_val
                eval_vector.append('Corr')
                original_time_diff_considered.append(original_pitches_timediff[original_cursor])
                played_time_diff_considered.append(played_pitches_timediffs[played_cursor])
                index_register.append(original_cursor)
                played_index_register.append(played_cursor)
                original_cursor +=1

            elif played_pitches[played_cursor] == original_pitches[original_cursor +1]:
                
                pitch_score +=ok_pitch_val
                eval_vector.append('n+1')
                original_cursor +=2
                
            elif played_pitches[played_cursor] == original_pitches[original_cursor -1]:
                
                pitch_score +=ok_pitch_val
                eval_vector.append('n-1')
                original_cursor = original_cursor
                
            elif played_pitches[played_cursor] == original_pitches[original_cursor -2]:
                
                pitch_score +=ok_pitch_val
                eval_vector.append('n-2')
                original_cursor -=1
                
            else:
                eval_vector.append('Incor')
                original_cursor +=1
            
        if original_cursor == original_pitches.size:
            break

    abs_pitch_score = pitch_score/played_pitches.size
    print(f'The Pitch score for this reproduction is {abs_pitch_score:.2f} out of 100 points \n')  
        
    print('The Pitch vector for this reproduction is:\n',eval_vector)
    #eval_vector

    print("\nThe Pitch vector's lenght is: ",len(eval_vector))
    print("\nThe sequence of the original song's indexes considered to build time differences is:\n",index_register)
    print("\nThe original time difference vector that will be used is:\n",np.around(original_time_diff_considered, decimals=3))
    print("\nThe sequence of the played song's indexes considered to build time differences is:\n",played_index_register)
    print("\nAnd the played time difference vector that will be used is:\n",np.around(played_time_diff_considered, decimals=3))

    # Standardized array of the original and played times (to properly evaluate slower reproductions)
    original_standard_time_diff = original_time_diff_considered / np.sum(original_time_diff_considered)
    played_standard_time_diff = played_time_diff_considered / np.sum(played_time_diff_considered)

    print("\n The standardized original time difference vector that will be used is:\n",np.around(original_standard_time_diff, decimals=3))
    print("\nAnd the standardized played time difference vector that will be used is:\n",np.around(played_standard_time_diff, decimals=3))

    result_array = played_standard_time_diff / original_standard_time_diff

    print("\nPartial percentual differences for each pitch are:\n",np.around(result_array, decimals=3))

    # Apply scoring system for time differences

    scoring_array = np.where(
        (np.abs(result_array - 1) <= perfect_time_umbral),  # Condition for 100 points
        perfect_time_val,
        np.where(
            ((np.abs(result_array - 1) <= ok_time_umbral) & (np.abs(result_array - 1) > perfect_time_umbral)),  # Condition for 80 points
            ok_time_val,
            0  # Default condition for 0 points
        )
    )


    print("\nPartial scores for timing on each pitch are:\n",np.around(scoring_array, decimals=2))

    time_score = np.mean(scoring_array)
    print(f'The time score for this reproduction is {time_score:.2f} out of 100 points \n')


    # Define cutting values for the scoring system
    low_cutoff = 40
    high_cutoff = 70

    def categorize_score(score, low_cutoff, high_cutoff):
        if score >= high_cutoff:
            return "high"
        elif score >= low_cutoff:
            return "medium"
        else:
            return "low"



    pitch_category = categorize_score(abs_pitch_score, low_cutoff, high_cutoff)
    print(f"In_function_Pitch Score: {abs_pitch_score:.0f}, Pitch Category: {pitch_category}")

    time_category = categorize_score(time_score, low_cutoff, high_cutoff)
    print(f"In_function_Time Score: {time_score:.0f}, Time Category: {time_category}")

    return abs_pitch_score, pitch_category, time_score, time_category



# I need to write the conditions for each combination of results, so I display the proper screen.
# one more click should restart the program so it excecutes again.
# that would finish the coding