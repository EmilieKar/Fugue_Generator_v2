# ==============================================
# Document for all different fitness functions.
# ==============================================

import numpy as np
import copy
from mingus.containers import *
import track_tests as measure
import track_functions as Track_Functions

# Points given to different note durations:
points_duration = {16:   1/32, 
                    8:    1/4, 
                    16/3: 2/32, 
                    4:    1, 
                    8/3:  1/4, 
                    2:    1, 
                    4/3:  2/4, 
                    1:    1/2}

points_duration_ending = {16:   1/64, 
                            8:    1/8, 
                            16/3: 2/64, 
                            4:    1, 
                            8/3:  1/8, 
                            2:    2, 
                            4/3:  2/4, 
                            1:    1/2}
        
accepted_durations = [16, 8, 16/3, 4, 8/3, 2, 4/3, 1]

# VARIABLES TO CHANGE: These are the "perfect" values
# frac = fraction/percentage of ...., nmb = number of...., rep = repetitions
frac_repeating_note_length = 0.5   
nmb_chords_between_tracks = 4.0
nmb_note_length_clusters = 4.0
nmb_of_passage_rep = 1.0
len_of_passage_rep = 3.0
frac_same_pattern = 0.85

# Helper funtion, creates and adds punishments for differing from "perfect values"
def near_calc(population_value, perfect_value, bias):
    return abs(population_value - perfect_value) * bias *(-1.0)
         
# The bigger the fraction the bigger the reward/punishment is
def more_calc(population_fraction, bias):
    return population_fraction * bias

# Favor notes close to C-4
def calculate_fitness_C(population, nr_bars):
        population_size = len(population)
        fitness_values = np.zeros(population_size)
        for iPop in range(population_size):
            melody = population[iPop]
            fitness = 0
            notes = melody.get_notes()
            
            for note in notes:
                if note[-1] is None:
                        fitness += (1/note[1])*1/nr_bars
                else:
                    distance = Note('C').measure(note[-1][0])
                    fitness += (note[1] * 10*abs(distance))/nr_bars

            if fitness == 0:
                fitness_values[iPop] = 2
            else:
                fitness_values[iPop] = 1/fitness
        
        return fitness_values

# Favor rests before notes with pitch
def calculate_fitness_rests(population):
    population_size = len(population)
    fitness_values = np.zeros(population_size)
    for iPop in range(population_size):
        melody = population[iPop]
        fitness = 0
        notes = melody.get_notes()
        
        for note in notes:
            if note[-1] is None:
                    fitness += 1/note[1]
                    
        fitness_values[iPop] = fitness
    return fitness_values

    
# A fitness function for modulating/binding together two bars 
def calculate_fitness_modulate(population, from_bar, to_bar, is_complex = True):
    "Return a melody that modulates from from_bar to to_bar"
    
    if is_complex:
        # Create a list of melodies including the bar before, the generated melody and the bar after.
        melodies = []
        track_from_bar = Track().add_bar(from_bar)
        track_to_bar = Track().add_bar(to_bar)
        for melody in population:
            track = copy.deepcopy(track_from_bar)
            Track_Functions.add_tracks(track, melody)
            Track_Functions.add_tracks(track, track_to_bar)
            melodies.append(track)

        population_size = len(population) 
        fitness_values = np.zeros(population_size) 
        
        default_bias = 10.0
        #For every melody in population calculate fitness THIS IS THE BIG CALCULATION PART
        for iPop in range(population_size):
            melody = melodies[iPop]
            notes = melody.get_notes()
            fitness = 1.0
            
            #----------------------------------------------------------------------------------------------------------------    
            #Measure closeness to ideal value
            
            #Within the melody
            #Function that measures:                                                   Ideal value:                    Bias:
            fitness += near_calc(measure.repeating_note_length(melody),                frac_repeating_note_length,     default_bias)
            fitness += near_calc(measure.average_note_length_clusters(melody),         nmb_note_length_clusters,       default_bias)
            (x,y,frac_repeating_passage) = measure.repeating_passages(melody)
            fitness += near_calc(x,                                                    nmb_of_passage_rep,             default_bias)
            fitness += near_calc(y,                                                    len_of_passage_rep,             default_bias) 
            
            #-----------------------------------------------------------------------------------------------------------------
            #Function that calculates fraction where 1 is best                          Bias:
            fitness += more_calc(frac_repeating_passage,                                default_bias) #Calculated previously
            (on_beat,on_half_beat) = measure.count_notes_on_beat(melody)
            #When multiplying or dividing the default bias we change the relative weight of that function
            fitness += more_calc(on_beat,                                               default_bias*2)
            fitness += more_calc(on_half_beat,                                          default_bias/2)

            fitness -= more_calc(measure.repeating_note_pitch(melody,True),             default_bias)
            fitness -= more_calc(measure.count_tritone_or_seventh_in_two_skips(melody), default_bias*1.2)
                
            fitness += more_calc(measure.check_melody_intervals(melody),                default_bias*5)
            fitness += more_calc(measure.check_motion_of_melody(melody),                default_bias*5)
            
            durations = measure.check_note_durations(melody)
            for iDur in accepted_durations:
                fitness += more_calc(durations[iDur],     points_duration[iDur] *       default_bias)

            #Add resulting fitness value to list
            fitness_values[iPop] = fitness
            
            
        return fitness_values 
    else:

        return calculate_fitness_C(population, 2)   
    
    
def calculate_fitness_harmony(population, input_melody, key, counter = False):

    if len(input_melody) == 0:
        print('Wrong input in fitness function')
        
    population_size = len(population) 
    fitness_values = np.zeros(population_size) 

    default_bias = 10.0
        
    #For every melody in population calculate fitness THIS IS THE BIG CALCULATION PART
    for iPop in range(population_size):
        melody = population[iPop]
        notes = melody.get_notes()
        fitness = 1.0
        #----------------------------------------------------------------------------------------------------------------    
        #Measure closeness to ideal value
        
        #Within the melody
        #Function that measures:                                                   Ideal value:                    Bias:
        fitness += near_calc(measure.repeating_note_length(melody),                frac_repeating_note_length,     default_bias)
        fitness += near_calc(measure.average_note_length_clusters(melody),         nmb_note_length_clusters,       default_bias)
        (x,y,frac_repeating_passage) = measure.repeating_passages(melody)
        fitness += near_calc(x,                                                    nmb_of_passage_rep,             default_bias)
        fitness += near_calc(y,                                                    len_of_passage_rep,             default_bias)
        
        # Between the melodies
        
        # Can be used here instead if wanting a lower amount of same pattern than 1
        #fitness += near_calc(measure.check_same_pattern(input_melody, melody),     frac_same_pattern,              default_bias)
        
        #-----------------------------------------------------------------------------------------------------------------
        #Function that calculates fraction where 1 is best                          Bias:
        fitness += more_calc(frac_repeating_passage,                                default_bias) #Calculated previously
        (on_beat,on_half_beat) = measure.count_notes_on_beat(melody)
        fitness += more_calc(on_beat,                                               default_bias*2)
        fitness += more_calc(on_half_beat,                                          default_bias/2)

        fitness += more_calc(measure.count_notes_in_scale(melody, key),             default_bias*5)
        fitness += more_calc(measure.check_same_pattern(input_melody, melody),      default_bias)

        consonant, too_long = measure.check_if_intervals_are_consonant_or_too_big(input_melody, melody)
        fitness += more_calc(consonant,                                             default_bias*2)
        fitness -= more_calc(too_long,                                              default_bias*5)

        fitness -= more_calc(measure.repeating_note_pitch(melody,True),             default_bias)
        fitness -= more_calc(measure.count_tritone_or_seventh_in_two_skips(melody), default_bias*1.2)
        
        fitness += more_calc(measure.check_melody_intervals(melody),                default_bias*1.2)
        fitness += more_calc(measure.check_motion_of_melody(melody),                default_bias*1.2)
               
        contrapuntal_motion_values = measure.contrapuntal_motion(input_melody, melody)
        fitness += more_calc(contrapuntal_motion_values['Contrary'],                default_bias*2)
        
        # If included, should add less than Contrary. Contrary is good, oblique and similar is okay.
        fitness += more_calc(contrapuntal_motion_values['Oblique'],                 default_bias*1.2)
        fitness += more_calc(contrapuntal_motion_values['Similar'],                 default_bias*1.2)
        
        # Having parallel motion or rest in both tracks is considered bad.
        fitness -= more_calc(contrapuntal_motion_values['Parallel'],                default_bias*3)
        fitness -= more_calc(contrapuntal_motion_values['Rest'],                    default_bias)
               
        durations = measure.check_note_durations(melody)
        for iDur in accepted_durations:
            fitness += more_calc(durations[iDur],     points_duration[iDur]       * default_bias*4)

        #Add resulting fitness value to list
        fitness_values[iPop] = fitness

    return fitness_values


def calculate_fitness_harmony_and_modulate(population, from_bar, to_bar, input_melody, key, counter = False):
    "Return a melody that modulates from from_bar to to_bar and harmonizes the input_melody"
    

    if len(input_melody) == 0:
        print('Wrong input in fitness function')

    # Create a list of melodies including the bar before, the generated melody and the bar after.
    melodies = []
    track_from_bar = Track().add_bar(from_bar)
    track_to_bar = Track().add_bar(to_bar)
    for melody in population:
        track = copy.deepcopy(track_from_bar)
        Track_Functions.add_tracks(track, melody)
        Track_Functions.add_tracks(track, track_to_bar)
        melodies.append(track)

    population_size = len(population) 
    fitness_values = np.zeros(population_size) 
    
    default_bias = 10.0


    #For every melody in population calculate fitness THIS IS THE BIG CALCULATION PART
    for iPop in range(population_size):
        melody = melodies[iPop]
        notes = melody.get_notes()
        fitness = 1.0
        
        #----------------------------------------------------------------------------------------------------------------    
        #Measure closeness to ideal value
        
        #Within the melody
        #Function that measures:                                                   Ideal value:                    Bias:
        fitness += near_calc(measure.repeating_note_length(melody),                frac_repeating_note_length,     default_bias)
        fitness += near_calc(measure.average_note_length_clusters(melody),         nmb_note_length_clusters,       default_bias)
        (x,y,frac_repeating_passage) = measure.repeating_passages(melody)
        fitness += near_calc(x,                                                    nmb_of_passage_rep,             default_bias)
        fitness += near_calc(y,                                                    len_of_passage_rep,             default_bias) 
        
        #-----------------------------------------------------------------------------------------------------------------
        #Function that calculates fraction where 1 is best                          Bias:
        fitness += more_calc(frac_repeating_passage,                                default_bias) #Calculated previously
        (on_beat,on_half_beat) = measure.count_notes_on_beat(melody)
        #When multiplying or dividing the default bias we change the relative weight of that function
        fitness += more_calc(on_beat,                                               default_bias*2)
        fitness += more_calc(on_half_beat,                                          default_bias/2)

        fitness += more_calc(measure.count_notes_in_scale(melody, key),             default_bias*5)
        fitness += more_calc(measure.check_same_pattern(input_melody, melody),      default_bias)

        consonant, too_long = measure.check_if_intervals_are_consonant_or_too_big(input_melody, melody)
        fitness += more_calc(consonant,                                             default_bias*2)
        fitness -= more_calc(too_long,                                              default_bias*5)

        fitness -= more_calc(measure.repeating_note_pitch(melody,True),             default_bias)
        fitness -= more_calc(measure.count_tritone_or_seventh_in_two_skips(melody), default_bias*1.2)
            
        fitness += more_calc(measure.check_melody_intervals(melody),                default_bias*5)
        fitness += more_calc(measure.check_motion_of_melody(melody),                default_bias*5)

        contrapuntal_motion_values = measure.contrapuntal_motion(input_melody, melody)
        fitness += more_calc(contrapuntal_motion_values['Contrary'],                default_bias*2)
        
        # If included, should add less than Contrary. Contrary is good, oblique and similar is okay.
        fitness += more_calc(contrapuntal_motion_values['Oblique'],                 default_bias*1.2)
        fitness += more_calc(contrapuntal_motion_values['Similar'],                 default_bias*1.2)
        
        # Having parallel motion or rest in both tracks is considered bad.
        fitness -= more_calc(contrapuntal_motion_values['Parallel'],                default_bias*3)
        fitness -= more_calc(contrapuntal_motion_values['Rest'],                    default_bias)
        
        durations = measure.check_note_durations(melody)
        for iDur in accepted_durations:
            fitness += more_calc(durations[iDur],     points_duration_ending[iDur] *       default_bias)

        #Add resulting fitness value to list
        fitness_values[iPop] = fitness
        
        
    return fitness_values