# STAGE 3: Comparison and scoring algorithm

import pandas as pd
import numpy as np
from more_itertools import pairwise
import os


def calculate_scores_from_arrays(original_pitches, played_pitches, original_timediff, played_timediff):
    """Pure scoring algorithm - no file I/O.

    Parameters
    ----------
    original_pitches  : np.ndarray  MIDI pitch values from the reference song
    played_pitches    : np.ndarray  MIDI pitch values detected from the player
    original_timediff : np.ndarray  inter-note time differences for the reference
    played_timediff   : np.ndarray  inter-note time differences for the played version

    Returns
    -------
    (abs_pitch_score, pitch_category, time_score, time_category)
    """

    print('There are ', original_pitches.size, ' pitches in the song')
    print('And they will be compared to ', played_pitches.size, ' pitches in the played song')
    print('There are ', original_timediff.size, ' time-differences in the song')
    print('And they will be compared to ', played_timediff.size, ' time-differences in the played song')

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

        if played_cursor == 0:

            if played_pitches[played_cursor] == original_pitches[original_cursor]:

                pitch_score += perfect_pitch_val
                eval_vector.append('Corr')
                original_cursor += 1


            elif played_pitches[played_cursor] == original_pitches[original_cursor + 1]:

                pitch_score += ok_pitch_val
                eval_vector.append('n+1')
                original_cursor += 2

            else:
                eval_vector.append('Incor')
                original_cursor += 1


        elif played_cursor == 1:

            if played_pitches[played_cursor] == original_pitches[original_cursor]:

                pitch_score += perfect_pitch_val
                eval_vector.append('Corr')
                original_time_diff_considered.append(original_timediff[original_cursor])
                played_time_diff_considered.append(played_timediff[played_cursor])
                index_register.append(original_cursor)
                played_index_register.append(played_cursor)
                original_cursor += 1


            elif played_pitches[played_cursor] == original_pitches[original_cursor + 1]:

                pitch_score += ok_pitch_val
                eval_vector.append('n+1')
                original_cursor += 2

            elif played_pitches[played_cursor] == original_pitches[original_cursor - 1]:

                pitch_score += ok_pitch_val
                eval_vector.append('n-1')
                original_cursor += 0

            else:
                eval_vector.append('Incor')
                original_cursor += 1

        else:

            if played_pitches[played_cursor] == original_pitches[original_cursor]:

                pitch_score += perfect_pitch_val
                eval_vector.append('Corr')
                original_time_diff_considered.append(original_timediff[original_cursor])
                played_time_diff_considered.append(played_timediff[played_cursor])
                index_register.append(original_cursor)
                played_index_register.append(played_cursor)
                original_cursor += 1

            elif played_pitches[played_cursor] == original_pitches[original_cursor + 1]:

                pitch_score += ok_pitch_val
                eval_vector.append('n+1')
                original_cursor += 2

            elif played_pitches[played_cursor] == original_pitches[original_cursor - 1]:

                pitch_score += ok_pitch_val
                eval_vector.append('n-1')
                original_cursor = original_cursor

            elif played_pitches[played_cursor] == original_pitches[original_cursor - 2]:

                pitch_score += ok_pitch_val
                eval_vector.append('n-2')
                original_cursor -= 1

            else:
                eval_vector.append('Incor')
                original_cursor += 1

        if original_cursor == original_pitches.size:
            break

    abs_pitch_score = pitch_score / played_pitches.size
    print('The Pitch score for this reproduction is {:.2f} out of 100 points \n'.format(abs_pitch_score))

    print('The Pitch vector for this reproduction is:\n', eval_vector)

    print("\nThe Pitch vector's lenght is: ", len(eval_vector))
    print("\nThe sequence of the original song's indexes considered to build time differences is:\n", index_register)
    print("\nThe original time difference vector that will be used is:\n", np.around(original_time_diff_considered, decimals=3))
    print("\nThe sequence of the played song's indexes considered to build time differences is:\n", played_index_register)
    print("\nAnd the played time difference vector that will be used is:\n", np.around(played_time_diff_considered, decimals=3))

    # Standardized array of the original and played times (to properly evaluate slower reproductions)
    original_standard_time_diff = original_time_diff_considered / np.sum(original_time_diff_considered)
    played_standard_time_diff = played_time_diff_considered / np.sum(played_time_diff_considered)

    print("\n The standardized original time difference vector that will be used is:\n", np.around(original_standard_time_diff, decimals=3))
    print("\nAnd the standardized played time difference vector that will be used is:\n", np.around(played_standard_time_diff, decimals=3))

    result_array = played_standard_time_diff / original_standard_time_diff

    print("\nPartial percentual differences for each pitch are:\n", np.around(result_array, decimals=3))

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

    print("\nPartial scores for timing on each pitch are:\n", np.around(scoring_array, decimals=2))

    time_score = np.mean(scoring_array)
    print('The time score for this reproduction is {:.2f} out of 100 points \n'.format(time_score))

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
    print("In_function_Pitch Score: {:.0f}, Pitch Category: {}".format(abs_pitch_score, pitch_category))

    time_category = categorize_score(time_score, low_cutoff, high_cutoff)
    print("In_function_Time Score: {:.0f}, Time Category: {}".format(time_score, time_category))

    return abs_pitch_score, pitch_category, time_score, time_category


def calculate_scores():
    """Read reference and recorded CSVs from disk and delegate to calculate_scores_from_arrays()."""

    print("Opening the csv register of the original song")
    from config import SONG_NAME, MIDI_CSV_DIR, RECORDED_TUNES_DIR
    song_name = SONG_NAME

    correct_song = pd.read_csv(MIDI_CSV_DIR / (song_name + '.csv'))
    print("Original song succesfully retrieved")

    print("Opening Transcription of the played song (for comparison)")
    recorded_song = pd.read_csv(RECORDED_TUNES_DIR / (song_name + '_for_comparison.csv'))
    print("Trasncription succesfully retrieved")

    return calculate_scores_from_arrays(
        correct_song['pitches'].to_numpy(),
        recorded_song['Pitch (MIDI)'].to_numpy(),
        correct_song['start_diff'].to_numpy(),
        recorded_song['Time difference (s)'].to_numpy(),
    )
