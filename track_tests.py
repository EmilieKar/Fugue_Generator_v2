#---------------------------------------------
# In this file we create different functions that verifies or measure different aspects of tracks 
# Basically a huge helper file for creating fitness functions later on
#---------------------------------------------

from mingus.containers import Track
from mingus.containers import Bar
from mingus.containers import NoteContainer
from mingus.containers import Note
import mingus.core.intervals as intervals
import mingus.core.notes as notes
import mingus.core.scales as scales
import mingus.core.keys as keys
import copy
import random
import track_functions as Track_Functions

"""FUNCTION INDEX                                           (to be able to find functions easier)
repeating_note_length(track)                                Calculates a fraction between the nmb of notes and the most occuring note length and returns it
average_numb_of_chords(track1,track2)                       Returns an average numb of chords/bar created by two tracks playing simultaneously
average_note_length_cluster(track)                          Returns the average size of same length note clusters
repeating_note_pitch(track, (optional bool exact))          Calculates a fraction between the nmb of notes and the most occuring note pitch and returns it
repeating_passages(track, (optional bool with_duration))    Returns (average_nm_of_rep,average_len_of_repetition,(percentage_of_repetition- kinda works but not perfect))
count_notes_on_beat(track)                                  Calculates how many notes that are on a beat of its own duration beats, or if it is in the middle of two such beats.
count_notes_in_scale(track)                                 Counts the number of notes in the track that is in the correct scale.
count_tritone_or_seventh_in_two_skips(track)                Returns the number of tritones or sevenths in two skips in a one-voice track.
contrapuntal_motion(track)                                  Returns dict with percentage of different contrapuntal motions used.
motion_of_track(track)                                      Returns list of which motions are in which part of track (Up, Down or Same).
check_parallell_and_similar(first_voice, second_voice, 
    start_beat, end_beat)                                   Returns dict with nr of beats of track having parallel and similar motion, and nr of beats with both.
get_all_intervals(first_voice, second_voice, 
    start_beat = 0, end_beat = None)                        Returns a list of two list, where the first contains all interval lengths in halvnote steps and the second list contains the duration of the interval in beats.
check_if_intervals_are_consonant_or_too_big(track1, track2) Returns list of the percentage of the tracks that have consonant intervals, and the percentage that have too big intervals.
check_same_pattern(track1, track2)                          Returns the percentage of the tracks that have the same note duration pattern.
count_fraction_of_good_melody_intervals(track)              Returns the percentage of good intervals in a melody
check_note_durations(track)                                 Returns dict with number of notes of different accepted durations and the number of notes having other durations.
"""

#--------------------------------------------------------------------
# repeating_note_length:
# Calculates a fraction between the nmb of notes and the most occuring note length and returns it
# Ex. If 60% of the notes are quarter notes the function will return 0.6
#--------------------------------------------------------------------
def repeating_note_length(track):
    note_generetor = copy.deepcopy(track).get_notes()
    #Dictionary that matches note length to nmb of occurences of that note
    note_lengths = {}
    #nmb of notes in track
    nmb_of_notes = 0.0

    for note in note_generetor:
        #If note length is not in dictionary add it
        if not(note[1] in note_lengths):
            note_lengths[note[1]] = 0.0
        #increment nmb of occurences and total number of notes
        note_lengths[note[1]] += 1.0
        nmb_of_notes += 1.0
    
    #Calculate the biggest fraction between occurences and nmb of notes in track
    biggest_fraction = 0.0
    for lengths,occurences in note_lengths.items():
        temp = occurences/nmb_of_notes
        if temp > biggest_fraction:
            biggest_fraction = copy.deepcopy(temp)

    return biggest_fraction

#--------------------------------------------------------------------
# average_numb_of_chords:
# Returns an average numb of chords/bar created by two tracks playing simultaneously
# TODO fix merge so that it doesn't cut length but doubles note instead
#--------------------------------------------------------------------
def average_numb_of_chords(track1, track2):
    #Use help function merge tracks to create a track were notes from both tracks are merged into note containers
    merged_track = Track_Functions.merge_tracks(track1,track2)
    note_generetor = merged_track.get_notes()
    numb_of_chords = 0.0

    for note in note_generetor:
        #If note is a pause skip
        if note[-1] is None:
            continue
        #If note container contains more than one note (a chord) increment chord counter
        if len(note[-1]) > 1:
            numb_of_chords += 1.0
    
    #Return average amount of chords/ bar
    return (numb_of_chords/ len(merged_track))

#--------------------------------------------------------------------
# average_note_length_cluster:
# returns the average size of same length note clusters (average number of notes in sequence to have the same note duration)
#--------------------------------------------------------------------
def average_note_length_clusters(track):
    note_generetor = copy.deepcopy(track).get_notes()
    nmb_of_notes = 1.0
    #List with length of all note-length clusters saved sequentially
    cluster_length = [1.0]
    curent_note_length = next(note_generetor)[1]

    for note in note_generetor:
        #If note is part of current cluster increment value
        if note[1] == curent_note_length:
            cluster_length[-1] += 1.0
        #Otherwise start new cluster
        else:
            curent_note_length = note[1]
            cluster_length.append(1.0)
    
    #Add all cluster lengths together
    added_cluster_legths = 0.0
    for length in cluster_length:
        added_cluster_legths += length
        
    #return average cluster length
    return (added_cluster_legths/len(cluster_length))

#--------------------------------------------------------------------
# repeating_note_pitch:
# Calculates a fraction between the nmb of notes and the most occuring note pitch and returns it
# exact is a bool that determines if you differ C-5, C, and Cb or consider them to be the same
#--------------------------------------------------------------------    
def repeating_note_pitch(track, exact = False):
    note_generetor = copy.deepcopy(track).get_notes()
    #Dictionary that matches note pitch to nmb of occurences of that note
    note_pitches = {}
    #nmb of notes in track
    nmb_of_notes = 0.0

    for note in note_generetor:
        if note[-1] is None:
            continue
        #If note pitch is not in dictionary add it
        nc = note[-1]
        for note_pitch in nc:
            if exact:
                if not(note_pitch.name in note_pitches):
                    note_pitches[note_pitch.name] = 0.0
                note_pitches[note_pitch.name] += 1.0
            else:
                if not(note_pitch.name[0] in note_pitches):
                    note_pitches[note_pitch.name[0]] = 0.0
                note_pitches[note_pitch.name[0]] += 1.0
        
        nmb_of_notes += 1.0
    
    #Calculate the biggest fraction between occurences and nmb of notes in track
    biggest_fraction = 0.0
    for pitches,occurences in note_pitches.items():
        temp = occurences/nmb_of_notes
        if temp > biggest_fraction:
            biggest_fraction = copy.deepcopy(temp)

    return biggest_fraction

#--------------------------------------------------------------------
# repeating_passages: (Values may not be exact but are good enough to use in the fitness function)
# Calculates average length of repeating passage, 
# Calculate average numb of repetitions of passages larger than 1 note
# Calculate the precentage of the track that is build up of repetition 
# Note: Repetitions are measured within a bar, witdh_duration determines if repetition has to have same relative note duration or not.
#--------------------------------------------------------------------   
def repeating_passages(track, with_duration = False):
    note_generetor = copy.deepcopy(track).get_notes()
    passage_repetitions = {}    #directory of occurences of different passages (nmb of repetitions)
    passage_lengths = {}        #directory of passage lenths, Cause you can't store two different values to same key in one directory
    current_passage = []        #List of either just (intervals as ints) or (intervals,relative difference between note durations)
    previous_note = None        
    previous_note_length = 0    #Only useful when considering note durations
    nmb_of_notes = 0.0          #Used to calculate percentage
    
    
    for note in note_generetor:
        nmb_of_notes += 1.0
        #If pause go to next note
        if note[-1] is None:
            continue
        
        #If new bar or first Note, change previous note to be the current note
        elif(note[0] == 0.0) or (previous_note is None):
            previous_note = note[-1][0]
            previous_note_length = note[1]
            current_passage = []
            continue

        else:
            #Calculate inteval as an int (works over octaves)
            diff = Note.measure(previous_note,note[-1][0])

            #If we have to take duration into consideration calculate relative duration
            #ev. TODO not precicely what it does but allows repetitions with all same note duration pass
            if with_duration:
                current_passage.append([diff, (previous_note_length - note[1])])
                previous_note_length = note[1]
            
            #If we don't consider duration just add interval
            else:
                current_passage.append(diff)

            #Set previous note to be current one
            previous_note = note[-1][0]
            
            #starting with the longes possible passage calculate the possible passages from current_passage
            for i in range(len(current_passage)):
                tmp = str(current_passage[i:len(current_passage)]) #key

                #if passage is already added increace occurance of passage
                if tmp in passage_repetitions:
                    passage_repetitions[tmp] += 1.0
                    break
                #If passage isn't added to dictionary, add it
                else: 
                    passage_repetitions[tmp] = 0.0
                    passage_lengths[tmp] = len(current_passage)- i + 1.0
            
    average_nm_of_rep = 0.0             #Will get the sum of all occurences
    average_len_of_repetition = 0.0     #Will get the sum of all passage length of repeated passages
    nmb_of_repeating_passages = 0.0     #Keeps track of the number of different repeated passages
    percentage_of_repetition = 0.0      #Will get the sum of all repeated notes

    for keys,occurences in passage_repetitions.items():
        if occurences > 0.0:
            average_nm_of_rep += occurences
            length_of_passage = passage_lengths[keys]
            percentage_of_repetition += (length_of_passage*occurences)
            average_len_of_repetition += length_of_passage
            nmb_of_repeating_passages += 1.0

    #Calculate final return data
    if nmb_of_repeating_passages > 0.0:
        average_nm_of_rep = average_nm_of_rep/nmb_of_repeating_passages
        average_len_of_repetition = average_len_of_repetition/nmb_of_repeating_passages
        percentage_of_repetition = percentage_of_repetition/nmb_of_notes #TODO percentage in faulty

    return (average_nm_of_rep,average_len_of_repetition,percentage_of_repetition)

#--------------------------------------------------------------------
# count_notes_on_beat:
# Calculates how many notes that are on a beat of its own duration beats, or 
# if it is in the middle of two such beats.
# Returns a tuple of the number of notes placed on correct beats, and the number 
# of notes in the middle of beats, normalized over total number of notes.
#--------------------------------------------------------------------   
def count_notes_on_beat(track):
    placed_on_beat = 0
    placed_on_half_beat = 0
    total_nr_of_notes = 0

    note_containers = track.get_notes()
    for note in note_containers:
        total_nr_of_notes += 1
        # Get the note from the container
        note_duration = note[1]
        note_beat = note[0]
        if (note_beat % (1/note_duration)) == 0:
            placed_on_beat += 1
        elif (note_beat % (1/(2*note_duration))) == 0:
            placed_on_half_beat += 1
    
    return (placed_on_beat/total_nr_of_notes, placed_on_half_beat/total_nr_of_notes)

#--------------------------------------------------------------------
# count_notes_in_scale:
# Counts the number of notes in the track that is in the correct scale.
# Returns the number of notes in scale normalized over total number of notes.
#--------------------------------------------------------------------   
def count_notes_in_scale(track, key):
    total_nr_of_notes = 0
    notes_in_scale = 0
    scale_notes = keys.get_notes(key)
    notes = track.get_notes()
    for note_container in notes:
        if note_container[-1] is None:
            total_nr_of_notes += 1
            continue
        note = note_container[-1][0]
        total_nr_of_notes += 1
        if note.name in scale_notes:
            notes_in_scale += 1
    
    return notes_in_scale/total_nr_of_notes

# ------------------------------------------
# count_tritone_or_seventh_in_two_skips(track): 
# Please feel free to rename !!
# Returns the number of tritones or sevenths in two skips in a one-voice track.
# Could be altered to return the indeces of the ugly intervals if that turns out to be useful.
# Limitation: if input has notecontainers with more than one pitch, it counts the first note in the container.
# -------------------------------------------
def count_tritone_or_seventh_in_two_skips(track, return_index = False):
    "Returns the number of tritones or sevenths in two skips in a one-voice track."
    
    unwanted_intervals = [6,10,11]  # tritone, minor and major seventh 
    
    # list of all notes
    notes = [track[i][j][2] for i in range(len(track.bars)) for j in range(len(track[i]))]

    # count nmb of unwanted intervals
    nmb = 0
    for i in range(len(notes)-2):
        note1 = notes[i]
        note2 = notes[i+2]
        if note1 is None or note2 is None:  # make sure notes aren't pauses
            continue
        interval = Note(note1[0]).measure(Note(note2[0]))   #returns the nmb. of halftones between the notes
        if abs(interval)%12 in unwanted_intervals:
                nmb += 1
    return nmb

# ---------------------------------------------
# contrapuntal_motion: 
# Measure what contrapuntal motion is used in the track.
# Returns a dictionary with percentage that the motion is used.
# The dictionary has the keys: 'Similar', 'Parallel', 'Oblique', 'Contrary', 'Rest' and 'One'.
# 'One' is for when only one voice have rest. 'Rest' is if both are resting.
# ---------------------------------------------
def contrapuntal_motion(first_voice, second_voice):
    if len(first_voice) == 0:
        print('Error occured')
        breakpoint()

    beat_first = 0
    beat_second = 0
    
    motion_first = motion_of_track(first_voice)
    motion_second = motion_of_track(second_voice)
    
    # Check combo of motions
    contrapuntal_motion = []
    parallel_motion = 0
    similar_motion = 0
    rest_motion = 0
    one_motion = 0
    oblique_motion = 0
    contrary_motion = 0
    
    extra_beats = 0
    
    previous_beat = 0   # Start of interval
    current_beat = min(motion_first[0][1], motion_second[0][1])     # End of interval
    total_nr_beats = len(first_voice)
    ind_first = 0
    ind_second = 0
    while previous_beat < total_nr_beats:
        if current_beat <= previous_beat:
            print(f"previous_beat: {previous_beat}")
            print(f"current_beat: {current_beat}")
            breakpoint()
        # Check if same motion in both tracks
        if motion_first[ind_first][-1] == motion_second[ind_second][-1]:
            # Check if both are resting
            if motion_first[ind_first][-1] == 'Rest':
                current_motion = 'Rest'
                rest_motion += current_beat - previous_beat
            else:
                # Check if parallel or similar
                parallel_and_similar = check_parallell_and_similar(first_voice, second_voice, previous_beat, current_beat)
                
                current_motion = 'Parallel and similar'
                parallel_motion += parallel_and_similar['Parallel']
                similar_motion += parallel_and_similar['Similar']
                try:
                    extra_beats += parallel_and_similar['Extra beats']
                except:
                    #breakpoint()
                    print('Error!')
                    breakpoint()
        
        # Check if one track is 'Same', then oblique
        elif motion_first[ind_first][-1] == 'Same' or motion_second[ind_second][-1] == 'Same':
            current_motion = 'Oblique'
            oblique_motion += current_beat - previous_beat
        # Check if one track is resting, then 'One'
        elif motion_first[ind_first][-1] == 'Rest' or motion_second[ind_second][-1] == 'Rest':
            current_motion = 'One'
            one_motion += current_beat - previous_beat
        # Otherwise motion is in opposite directions and contrary
        else:
            current_motion = 'Contrary'
            contrary_motion += current_beat - previous_beat
        
        # Add motion to list
        contrapuntal_motion.append([previous_beat, current_beat-previous_beat, current_motion])

        # If reach the end of track, break
        if current_beat == total_nr_beats:
            break
        
        # Update beats and indices
        previous_beat = current_beat # Updating previous_beat
        old_ind_first = ind_first
        if motion_first[ind_first][0] + motion_first[ind_first][1] == current_beat:
            # Take next part of motion_first
            ind_first += 1 
            
        if motion_second[ind_second][0] + motion_second[ind_second][1] == current_beat:
            # Take next part of motion_second
            ind_second += 1
        
        # Update previous beat to be the start of the motion that starts last.
        previous_beat = max(motion_first[ind_first][0], motion_second[ind_second][0])

        # Double the beats that are in two separate parts
        extra_beats += current_beat-previous_beat

        # Update current_beat to be the end of the note ending first of the two current notes
        current_beat = min(motion_first[ind_first][0] + motion_first[ind_first][1], motion_second[ind_second][0] + motion_second[ind_second][1])

        
    contrapuntal_motion_values = {'Contrary': contrary_motion/(total_nr_beats + extra_beats), 'Parallel': parallel_motion/(total_nr_beats + extra_beats), 
                    'Oblique': oblique_motion/(total_nr_beats + extra_beats), 'Similar': similar_motion/(total_nr_beats + extra_beats), 
                    'Rest': rest_motion/(total_nr_beats + extra_beats), 'One': one_motion/(total_nr_beats + extra_beats)}
    
    return contrapuntal_motion_values

# ---------------------------------------------
# track_motion: 
# Help function that gets a track as input and calculates how the motion is for different parts.
# Returns a list of list elements in the form [start, length, type], with start being the start of the 
# motion, length being the length of the motion in beats, and type is either 'Up', 'Down', 'Same' or 'Rest'.
# ---------------------------------------------
def motion_of_track(track):

    # Initialize lists to contain tuples of which beats contain which motion
    motion = []


    # Loop over all notes in first voice to decide motion
    notes = track.get_notes()

    previous_note = None
    current_passage = 0
    current_start = 0
    current_motion = None
    for note in notes:  

        # If first note in track
        if previous_note is None:
            # If not a rest, add to first part but set which motion later
            if not note[-1] is None:
                previous_note = note
                current_passage = 1/note[1]
                continue
            # If a rest, start a rest motion
            else:
                previous_note = note
                current_passage = 1/note[1]
                current_motion = 'Rest'
                continue
          
        # If the note is a rest, end last motion and start a rest motion
        if note[-1] is None:
            if current_motion != 'Rest':
                # Add the previous motion to the list. If None, set it to Same.
                if current_motion is None:
                    current_motion = 'Same'
                motion.append([current_start, current_passage, current_motion])                
                
                # Start new upward motion
                current_start += current_passage
                current_passage = 1/note[1]
                current_motion = 'Rest'
            else:
                current_passage += 1/note[1]
        # If last note was a rest, end rest motion and start new motion
        elif current_motion == 'Rest':
                motion.append([current_start, current_passage, current_motion])
                
                # Start new unknown motion
                current_start += current_passage
                current_passage = 1/note[1]
                current_motion = None
        
        # Upward motion between this and previous note
        elif note[-1][0] > previous_note[-1][0]:
            if current_motion == 'Up':
                current_passage += 1/note[1]                
            elif current_motion is None:
                current_motion = 'Up'
                current_passage += 1/note[1]                
            else:
                # Add the previous motion to the list
                motion.append([current_start, current_passage, current_motion])                
                
                # Start new upward motion
                current_start += current_passage - 1/previous_note[1]
                current_passage = 1/previous_note[1] + 1/note[1]
                current_motion = 'Up'
        
        # Downward motion between this and previous note
        elif note[-1][0] < previous_note[-1][0]:
            if current_motion == 'Down':
                current_passage += 1/note[1]                
            elif current_motion is None:
                current_motion = 'Down'
                current_passage += 1/note[1]                
            else:
                # Add the previous motion to the list
                motion.append([current_start, current_passage, current_motion])                
                
                # Start new upward motion
                current_start += current_passage - 1/previous_note[1]
                current_passage = 1/previous_note[1] + 1/note[1]
                current_motion = 'Down'
        
        # No motion between this and previous note
        elif note[-1][0] == previous_note[-1][0]:
            if current_motion == 'Same':
                current_passage += 1/note[1]                
            elif current_motion is None:
                current_motion = 'Same'
                current_passage += 1/note[1]                
            else:
                # Add the previous motion to the list
                motion.append([current_start, current_passage, current_motion])                
                
                # Start new upward motion
                current_start += current_passage - 1/previous_note[1]
                current_passage = 1/previous_note[1] + 1/note[1]
                current_motion = 'Same'
        
        previous_note = note
    
    # Add the previous motion to the list
    motion.append([current_start, current_passage, current_motion])                
    return motion
 
# ---------------------------------------------
# check_parallell_and_similar: 
# Help function that takes two tracks and a time span as input, and calculates how much of this part has similar and how much has parallel motion.
# Return a dictionary with keys 'Parallel' and 'Similar' with their respective number of beats having that motion. Also has a key 'Extra beats' with the number of overlapping beats.
# ---------------------------------------------
def check_parallell_and_similar(first_voice, second_voice, start_beat, end_beat):
    
    if len(first_voice) == 0:
        print('Error occured')
        breakpoint()

    # Get all intervals in this part, including the interval before the one at start_beat.
    intervals, interval_lengths = get_all_intervals(first_voice, second_voice, start_beat, end_beat)
    
    if len(intervals) == 1:
        return {'Parallel': 0, 'Similar': 0, 'Extra beats': 0}
    
    third_intervals = [3, 4]
    second_intervals = [1, 2]
    seventh_intervals = [10, 11]
    
    parallel_time = 0
    similar_time = 0
    previous_interval = intervals[0]
    previous_motion = None
    current_pass = 0
    extra_beats = 0
    for i in range(1,len(intervals)):
        # Check if minor of major third
        third_repeated = False
        if intervals[i] % 12 in third_intervals and previous_interval % 12 in third_intervals:
            if intervals[i] // 12 == previous_interval //12:
                third_repeated = True
        # Check if second
        second_repeated = False
        if intervals[i] % 12 in second_intervals and previous_interval % 12 in second_intervals:
            if intervals[i] // 12 == previous_interval //12:
                second_repeated = True
        # Check if seventh
        seventh_repeated = False
        if intervals[i] % 12 in seventh_intervals and previous_interval % 12 in seventh_intervals:
            if intervals[i] // 12 == previous_interval //12:
                seventh_repeated = True

        
        if intervals[i] == previous_interval or third_repeated or second_repeated or seventh_repeated:
            if previous_motion == 'parallel':
                current_pass += interval_lengths[i]
            else:
                if previous_motion == 'similar':
                    similar_time += current_pass
                    extra_beats += interval_lengths[i-1]
                previous_motion = 'parallel'
                current_pass = interval_lengths[i-1] + interval_lengths[i]
        else:
            if previous_motion == 'similar':
                current_pass += interval_lengths[i]
            else:
                if previous_motion == 'parallel':
                    parallel_time += current_pass
                    extra_beats += interval_lengths[i-1]
                previous_motion = 'similar'
                current_pass = interval_lengths[i-1] + interval_lengths[i]
    if previous_motion == 'similar':
        similar_time += current_pass
    else:
        parallel_time += current_pass

    if similar_time + parallel_time == 0:
        print(f"similar time: {similar_time}")
        print(f"parallel time: {parallel_time}")
        breakpoint()
    return {'Parallel': parallel_time, 'Similar': similar_time, 'Extra beats': extra_beats}
    
# ---------------------------------------------
# get_all_intervals: 
# Help function that takes two tracks and a time span as input, and finds all intervals in this part.
# Returns two lists. The first one with all intervals between the two tracks in halfnotes. 
# The second one with the length of all these intervals.
# ---------------------------------------------
def get_all_intervals(first_voice, second_voice, start_beat = 0, end_beat = None):
    """Returns two lists. The first one with all intervals between the two tracks in halfnotes. 
    The second one with the length of all these intervals.
    """

    if len(first_voice) == 0:
        print('Error occured')
        breakpoint()

    if end_beat is None:
        end_beat = min(len(first_voice), len(second_voice))
    
    
    # Get a generator for all notes in each track and skip to the notes at start_beat
    notes_first = first_voice.get_notes()
    notes_second = second_voice.get_notes()
    #breakpoint()
    first_beat = 0
    for note_first in notes_first:
        # If end of note is before beat, take the next note
        if first_beat + 1/note_first[1] <= start_beat:
            first_beat += 1/note_first[1]
            continue
        else:
            break

    second_beat = 0
    for note_second in notes_second:
        # If end of note is before beat, take the next note
        if second_beat + 1/note_second[1] <= start_beat:
            second_beat += 1/note_second[1]
            continue
        else:
            break
    
    # Find all intervals
    intervals = []
    interval_lengths = []
    beat = start_beat
    ind_first = 0
    ind_second = 0
    while beat < end_beat:
        # Find interval
        current_interval = Track_Functions.interval_at_beat(first_voice, second_voice, beat, return_int=True)
        
        # Save the interval
        intervals.append(current_interval)

        # Save beat as previous beat
        previous_beat = beat
        
        old_note_first = note_first
        old_first_beat = first_beat
        # Update beat and current notes
        if first_beat + 1/note_first[1] <= second_beat + 1/note_second[1]:
            first_beat += 1/note_first[1]
            beat = first_beat

            if first_beat == end_beat:
                interval_lengths.append(first_beat-previous_beat)
                break
            try:
                note_first = next(notes_first)
            except:
                print('Error now!')
                breakpoint()
            
        if old_first_beat + 1/old_note_first[1] >= second_beat + 1/note_second[1]:
            second_beat += 1/note_second[1]
            beat = second_beat

            if second_beat == end_beat:
                interval_lengths.append(second_beat-previous_beat)
                break
            note_second = next(notes_second)
        
        interval_lengths.append(beat-previous_beat)
         
    return [intervals, interval_lengths]

# ---------------------------------------------
# check_consonant_percentage:
# Takes two tracks as input and calculate the percentage of the track beats where it is consonant intervals bewteen the two tracks.
# Return a float with percentage.
# ---------------------------------------------
def check_if_intervals_are_consonant_or_too_big(track1, track2):
    
    # Get all intervals and their lengths
    intervals, interval_lengths = get_all_intervals(track1, track2)
    
    # Get a generator for all notes in each track and skip to the notes at start_beat
    #notes_first = track1.get_notes()
    #notes_second = track2.get_notes()
    
    #note_first = next(notes_first)
    #note_second = next(notes_second)
    
    consonant_total = 0
    over_maximum_interval = 0
    # Check all intervals
    #beat = min(1/note_first[1], 1/note_first[1])
    #bar_nr = 0
    #previous_beat = 0
    #end_beat = len(track1)  #nr of bars
    
    consonant_intervals = [0, 3, 4, 7, 8, 9]
    
    for i in range(len(intervals)):
        # If one of tracks is resting, continue
        if intervals[i] is None:
            continue
            
        if abs(intervals[i]) in consonant_intervals:
            consonant_total += interval_lengths[i]
        
        elif abs(intervals[i]) > 16:
            over_maximum_interval += interval_lengths[i]
            
    consonant_rate = consonant_total/len(track1)
    too_long_rate = over_maximum_interval/len(track1)
    
    return [consonant_rate, too_long_rate]


# ---------------------------------------------
# check_same_pattern:
# Takes two tracks as input and calculate the percentage of the track beats where both tracks have notes with same start beat and same duration.
# Return a float with percentage.
# ---------------------------------------------
def check_same_pattern(track1, track2):
    
    same_duration = 0
    
    notes_1 = [i for i in track1.get_notes()]
    notes_2 = [i for i in track2.get_notes()]
    
    ind_1 = 0
    ind_2 = 0    
    while ind_1 < len(notes_1) and ind_2 < len(notes_2):        
        beat_1 = notes_1[ind_1][0]
        beat_2 = notes_2[ind_2][0]
        if beat_1 < beat_2:
            # Skip to next note in track 1
            ind_1 +=1
            continue
        elif beat_2 < beat_1:
            # Skip to next note in track 2
            ind_2 +=1
            continue
        
        # Check if duration is equal
        if notes_1[ind_1][1] == notes_2[ind_2][1]:
            # Add the duration (in beats) to same_duration
            same_duration += 1/notes_1[ind_1][1]

        # Update indices and beats
        ind_1 += 1
        ind_2 += 1
        
    same_duration_percentage = same_duration/len(track1)
    
    return same_duration_percentage

# ------------------------------------------
# check_melody_intervals: 
# Checks what fraction of a melody that use 'good' intervals: No big jumps or dissonant intervals allowed,
# according to #2 in this list https://en.wikipedia.org/wiki/Counterpoint#Considerations_for_all_species
#
# Notes: Does not take tonality into account. If there are one or zero notes in the melody, it returns 0.
# ------------------------------------------
def check_melody_intervals(track):
    # The melody we test is the track melody without pauses. It will work if the melody has multiple pitches
    # in the same noteContainer, but it uses the first note in each container. A way to make it smarter would
    # be to use the highest pitch, but I don't think that's necessary for now
    melody = [note[2][0] for note in track.get_notes() if note[2]]
    good_intervals = [0,1,2,3,4,5,7,12]
    
    if len(melody) <= 1:
        return  0.0
    
    # count number of good intervals 
    nmb = 0
    for i in range(len(melody)-1):
        interval = Note(melody[i]).measure(Note(melody[i+1]))
        if abs(interval) in good_intervals:
            nmb += 1     # one point if good interval    
        
        elif interval in [8,9] and i+2 < len(melody):
            # if the interval was a sixth up, count as good only if it is followed by downward motion
            # (doesn't matter here what kind of downward motion - if it's 'good', it will get a point
            # in the next iteration of the loop)
            next_interval = Note(melody[i+1]).measure(Note(melody[i+2]))
            if next_interval < 0:
                nmb +=1

    # return fraction of good intervals in the melody
    return nmb / (len(melody)-1)

# ---------------------------------
#   check_motion_of_melody
#   counts skips/steps that are good according to counterpoint rules. a friend to the above function
#   check_melody_intervals, but this considers the general motion instead of definite intervals
#
#   notes & limitations: 
#       - doesn't consider disonances in two steps (this is handled by count_tritone_or_seventh...)
#       - only looks at the general motion of the melody, not if the intervals sound good 
#       (is partly handled by check_melody_intervals)
#       - the names of these functions could be better/clearer 
#  ---------------------------------
def check_motion_of_melody(track):
    melody = [note[2][0] for note in track.get_notes() if note[2]]    
    
    if len(melody) <= 1:
        return 0
    
    # Bool that makes sure all intervals are considered once
    skip_next_iteration = False

    # Variable to keep track on if the last two skips are in the same direction (and what direction)
    last_two_skips_dir = 0

    good = 0
    for i in range(len(melody)-1):
        if skip_next_iteration:             # This happens if the interval already is counted 
            skip_next_iteration = False
            continue 

        note1 = Note(melody[i])
        note2 = Note(melody[i+1])
        interval = note1.measure(note2)

        # Steps are always good        
        if abs(interval) <= 2:
            good += 1
            last_two_skips_dir = 0      # Reset two skip counter 
            continue
    
        # Skips are good depending on circumstances:            
        direction = interval / abs(interval)            # -1 if downward motion, 1 if upward
            
        # Bad, continue: Skip is in the same direction as previous two
        if direction == last_two_skips_dir:
            continue
        else:
            last_two_skips_dir = 0  # reset counter

        # Good: Skip is last interval of melody
        if i+2 >= len(melody):
            good += 1
            continue

        # At this point, there is not enough info to determine if the interval is good 
        # without looking at the next one            
        # --------- From here on we consider two intervals at a time ! ----------------
        skip_next_iteration = True      # So that the new interval is only counted once
        note3 = Note(melody[i+2])
        next_interval = note2.measure(note3)

        # Good : Skip - step
        if abs(next_interval) <= 2:
            good += 2
            continue

        # Good: Skip - Skip (in opposite directions)
        if direction != next_interval/abs(next_interval): 
            good += 2
            last_two_skips_dir = 0
        # Good: Skip - Skip (in same direction, if second skip is smaller than first)
        elif abs(next_interval) < abs(interval): 
            good += 2
            last_two_skips_dir = direction   # Save direction as warning 
        else:
            last_two_skips_dir = direction   # Save direction as warning

    frac_of_good_motion = good / (len(melody)-1)
    return frac_of_good_motion

# ---------------------------------------------
# check_note_durations:
# Check the duration of all notes.
# Returns a dict with the number of notes having the different accepted lengths, 
# and also the number of notes having strange durations.
# ---------------------------------------------
def check_note_durations(track):
    notes = track.get_notes()
    duration_counter = {16: 0, 8: 0, 16/3: 0, 4: 0, 8/3: 0, 2: 0, 4/3: 0, 1: 0, 'Strange': 0}
    for note in notes:
        duration = note[1]
        if not duration in duration_counter:
            duration_counter['Strange'] += 1
        else:
            duration_counter[duration] += 1
    
    return duration_counter
        
