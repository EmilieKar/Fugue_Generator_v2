#--------------------------------------------------------------
# This document works as the Main file for fugue generation
# Contains the global variables that defines the fugue, voices, key and subject
# The function generate_fugue generates an easy finished fugue composition
# The function generate_longer_fugue can generate a longer fugue with minor, reversed and/or inversed parts developments
#--------------------------------------------------------------

from mingus.containers import Composition
from mingus.containers import Bar
from mingus.containers import Track
from mingus.containers import Note
import mingus.core.intervals as intervals

import mingus.extra.lilypond as LilyPond
from Mingus_LilyPond_helper import to_LilyPond_file
import track_functions as Track_Functions
from mingus.midi import midi_file_out
import copy
from EvolutionaryGenerator import EvolutionaryGenerator
import random as rnd

#Important variables!
fugue = Composition()
first_voice = Track()
second_voice = Track()     
            
#input_key is a char signifying what key we are using
#input_subject is a Track, subject can be any length
def generate_fugue(key,subject):

    #If subject doesn't fill full bars fill out rest of last bar of subject with rest
    #if last bar is not full
    if not (subject[-1].is_full()): 
        #place a rest at the end of the last bar with the length of 1/(remaining fraction of bar)
        subject[-1].place_rest(int(1.0/subject[-1].space_left()))

    # Create first bar with subject in first voice and rest in second voice. 
    rest_1bar = Bar(key)
    rest_1bar.place_rest(1)
    first_voice = copy.deepcopy(subject)

    #Add same amount of "rest bars" as the number of bars in the subject
    for i in range(len(subject)):  
        second_voice.add_bar(copy.deepcopy(rest_1bar))
    

    # Create second bar with answer in second voice.
    answer = Track_Functions.create_answer(subject, key)
    
    #second_voice = second_voice + answer
    Track_Functions.add_tracks(second_voice,answer)
    
    # Generate countersubject
    eg_counter = EvolutionaryGenerator(key, nr_bars = 1, fitness_function = 'counter', input_melody = subject, nr_generations = counter_nr_generations)
    print('Generating evolutionary part 1 of 7')
    eg_counter.run_evolution()
    counter_subject = copy.deepcopy(eg_counter.best_individual)
    
    Track_Functions.add_tracks(first_voice, counter_subject)
    

    # Save bar 2 for later modulation
    bar_2 = first_voice[-1]    
    
    # Generate development in minor in bar 5 and 6. 
    # Transposed -3 to minor + (stämma i för second voice tills vidare tom)
    minor_first_voice = Track_Functions.transpose_to_relative_minor(first_voice, key, False)
    minor_second_voice = Track_Functions.transpose_to_relative_minor(second_voice, key, False)
        
    bar_5 = minor_first_voice[0]
    
    # Generate harmony in second voice in bar 5
    eg_harmony_minor = EvolutionaryGenerator(key, nr_bars = 1, fitness_function = 'harmony', 
            input_melody = Track().add_bar(copy.deepcopy(minor_first_voice[0])), nr_generations = harmony_nr_generations)
    
    print('Generating evolutionary part 2 of 7')
    eg_harmony_minor.run_evolution()
    
    minor_second_voice[0] = eg_harmony_minor.best_individual[0]

    # Generate bar 3 and 4 as a modulation between bar 2 and 5

    eg_modulate_to_minor = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'modulate', 
            from_bar = bar_2, to_bar = bar_5, nr_generations = modulate_nr_generations)

    print('Generating evolutionary part 3 of 7')
    eg_modulate_to_minor.run_evolution()
    modulate_first_voice = copy.deepcopy(eg_modulate_to_minor.best_individual)

    # Generate second voice as harmony to the first voice in bar 3 and 4
    
    eg_second_voice_modulate = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'harmony', 
            input_melody = modulate_first_voice, nr_generations = harmony_nr_generations)
    
    print('Generating evolutionary part 4 of 7')
    eg_second_voice_modulate.run_evolution()    
    modulate_second_voice = copy.deepcopy(eg_second_voice_modulate.best_individual)


    # Add bar 3-6 to the voice tracks
    Track_Functions.add_tracks(first_voice, modulate_first_voice)
    Track_Functions.add_tracks(second_voice, modulate_second_voice)
    
    Track_Functions.add_tracks(first_voice, minor_first_voice)
    Track_Functions.add_tracks(second_voice, minor_second_voice)

    bar_6 = first_voice[-1]

    # Create canon in bar 9 and 10.
    # subject i first voice
    # second voice is subject but shifted (half a bar for now) 

    canon_first_voice = Track()
    canon_first_voice.add_bar(copy.deepcopy(subject[0]))
    
    bar_9 = canon_first_voice[0]

    canon_second_voice = Track_Functions.shift(subject, 2)

    # Create modulation from minor to major in 7 and 8
    
    eg_modulate_to_major = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'modulate', 
            from_bar = bar_6, to_bar = bar_9, nr_generations = modulate_nr_generations)
    
    print('Generating evolutionary part 5 of 7')
    eg_modulate_to_major.run_evolution()
    modulate_back_first_voice = copy.deepcopy(eg_modulate_to_major.best_individual)

    # Generate second voice as harmony to the first voice in bar 7 and 8
    
    eg_second_voice_modulate_back = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'harmony', 
            input_melody = modulate_first_voice, nr_generations = harmony_nr_generations)
    
    print('Generating evolutionary part 6 of 7')
    eg_second_voice_modulate_back.run_evolution()    
    modulate_back_second_voice = copy.deepcopy(eg_second_voice_modulate.best_individual)
    
    
    # Add bar 7-10 to the voice tracks
    Track_Functions.add_tracks(first_voice, modulate_back_first_voice)
    Track_Functions.add_tracks(second_voice, modulate_back_second_voice)
    
    Track_Functions.add_tracks(first_voice, canon_first_voice)
    Track_Functions.add_tracks(second_voice, canon_second_voice)

    # Add cadence ending to second voice
    Track_Functions.second_voice_ending(second_voice, key)

    second_voice_ending = Track().add_bar(copy.deepcopy(second_voice[-3]))
    second_voice_ending.add_bar(copy.deepcopy(second_voice[-2]))
    
    # Generate harmony to cadence in first voice
    first_voice_last_bar = Track_Functions.first_voice_ending(first_voice, key)

    eg_first_voice_ending = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'ending', 
            input_melody = second_voice_ending, from_bar = subject[0], to_bar = first_voice_last_bar[0], nr_generations = harmony_nr_generations)

    print('Generating evolutionary part 7 of 7')
    eg_first_voice_ending.run_evolution()
    first_voice_ending = copy.deepcopy(eg_first_voice_ending.best_individual)
    Track_Functions.add_tracks(first_voice, first_voice_ending)
    Track_Functions.add_tracks(first_voice, first_voice_last_bar)
    
    #Add voices together to create a final composition
    fugue.add_track(first_voice)
    fugue.add_track(second_voice)

    #Generate lilypond file for fugue named final_fugue
    finished_fugue = LilyPond.from_Composition(fugue)
    to_LilyPond_file(finished_fugue,"final_fugue")

    #Generate MIDI output for fugue named final_fugue
    midi_file_out.write_Composition("final_fugue.mid", fugue)

 
# nr_parts tells how many parts (inverse, reverse, minor, other start note) is wanted between first subject/answer and the last stretto.
def generate_longer_fugue(key, subject, nr_parts = 1, order_of_parts = None):
    #If subject doesn't fill full bars fill out rest of last bar of subject with rest
    #if last bar is not full
    if not (subject[-1].is_full()): 
        #place a rest at the end of the last bar with the length of 1/(remaining fraction of bar)
        subject[-1].place_rest(int(1.0/subject[-1].space_left()))
    
    # Create first bar with subject in first voice and rest in second voice. 
    rest_1bar = Bar(key)
    rest_1bar.place_rest(1)
    first_voice = copy.deepcopy(subject)

    #Add same amount of "rest bars" as the number of bars in the subject
    for i in range(len(subject)):  
        second_voice.add_bar(copy.deepcopy(rest_1bar))
    
    total_nr_evolutionary_parts = 3 + 3*nr_parts

    # Create second bar with answer in second voice.
    answer = Track_Functions.create_answer(subject, key)
    
    Track_Functions.add_tracks(second_voice,answer)
    
    # Generate countersubject
    nr_current_generated = 1
    eg_counter = EvolutionaryGenerator(key, nr_bars = 1, fitness_function = 'counter', input_melody = subject, nr_generations = counter_nr_generations)
    print(f"Generating evolutionary part {nr_current_generated} of {total_nr_evolutionary_parts}")
    nr_current_generated += 1
    eg_counter.run_evolution()
    counter_subject = copy.deepcopy(eg_counter.best_individual)
    
    Track_Functions.add_tracks(first_voice, counter_subject)
    

    # Save subject, answer and countersubject
    first_voice_first_part = copy.deepcopy(first_voice)
    second_voice_first_part = copy.deepcopy(second_voice)
    
    # Save bar 2 for later modulation
    bar_prev = first_voice[-1]

    variants = ['Minor', 'Reverse', 'Inverse']
    iParts = 0
    
    if order_of_parts is None:
        order_of_parts = []
        for i in range(nr_parts):
            rVariant = rnd.choice(variants)
            order_of_parts.append(rVariant)
    
    
    while iParts < nr_parts:
            current_variant = order_of_parts[iParts]
            
            if current_variant == 'Minor':
                # Generate development in minor
                # Transposed -3 to minor (stämma i second voice tills vidare tom)
                new_first_voice = Track_Functions.transpose_to_relative_minor(first_voice, key, False)
                new_second_voice = Track_Functions.transpose_to_relative_minor(second_voice, key, False)
                    
                bar_after = new_first_voice[0]
            
                # Generate harmony in second voice first bar
                eg_harmony = EvolutionaryGenerator(key, nr_bars = 1, fitness_function = 'harmony', 
                        input_melody = Track().add_bar(copy.deepcopy(new_first_voice[0])), nr_generations = harmony_nr_generations)
                
                print(f"Generating evolutionary part {nr_current_generated} of {total_nr_evolutionary_parts}")
                nr_current_generated += 1
                eg_harmony.run_evolution()
                
                new_second_voice[0] = eg_harmony.best_individual[0]

            elif current_variant == 'Reverse':
                # Generate reverse development
                
                new_first_voice = Track_Functions.reverse(first_voice_first_part, key)
                new_second_voice = Track_Functions.reverse(second_voice_first_part, key)
                
                bar_after = new_first_voice[0]

                # Generate harmony in second voice first bar
                eg_harmony = EvolutionaryGenerator(key, nr_bars = 1, fitness_function = 'harmony', 
                        input_melody = Track().add_bar(copy.deepcopy(new_first_voice[1])), nr_generations = harmony_nr_generations)
                
                print(f"Generating evolutionary part {nr_current_generated} of {total_nr_evolutionary_parts}")
                nr_current_generated += 1
                eg_harmony.run_evolution()
                new_second_voice[1] = eg_harmony.best_individual[0]

            elif current_variant == 'Inverse':
                # Generate inverse development
                
                new_first_voice = Track_Functions.inverse(first_voice_first_part)
                new_second_voice = Track_Functions.inverse(second_voice_first_part)
                
                bar_after = new_first_voice[0]

                # Generate harmony in second voice first bar
                eg_harmony = EvolutionaryGenerator(key, nr_bars = 1, fitness_function = 'harmony', 
                        input_melody = Track().add_bar(copy.deepcopy(new_first_voice[0])), nr_generations = harmony_nr_generations)

                print(f"Generating evolutionary part {nr_current_generated} of {total_nr_evolutionary_parts}")
                nr_current_generated += 1
                eg_harmony.run_evolution()
                new_second_voice[0] = eg_harmony.best_individual[0]
                
                

            # Generate the two bars linking this new part to the previous parts

            eg_modulate = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'modulate', 
                    from_bar = bar_prev, to_bar = bar_after, nr_generations = modulate_nr_generations)

            print(f"Generating evolutionary part {nr_current_generated} of {total_nr_evolutionary_parts}")
            nr_current_generated += 1
            eg_modulate.run_evolution()
            modulate_first_voice = copy.deepcopy(eg_modulate.best_individual)

            # Generate second voice as harmony to this linking part
            
            eg_second_voice_modulate = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'harmony', 
                    input_melody = modulate_first_voice, nr_generations = harmony_nr_generations)
            
            print(f"Generating evolutionary part {nr_current_generated} of {total_nr_evolutionary_parts}")
            nr_current_generated += 1
            eg_second_voice_modulate.run_evolution()    
            modulate_second_voice = copy.deepcopy(eg_second_voice_modulate.best_individual)


            # Add new bars to the voice tracks
            Track_Functions.add_tracks(first_voice, modulate_first_voice)
            Track_Functions.add_tracks(second_voice, modulate_second_voice)
            
            Track_Functions.add_tracks(first_voice, new_first_voice)
            Track_Functions.add_tracks(second_voice, new_second_voice)

            bar_prev = first_voice[-1]
            
            iParts += 1
            

    # Create canon in bar 9 and 10.
    # subject i first voice
    # second voice is subject but shifted (half a bar for now) 

    canon_first_voice = Track()
    canon_first_voice.add_bar(copy.deepcopy(subject[0]))
    
    bar_after = canon_first_voice[0]

    canon_second_voice = Track_Functions.shift(subject, 2)

    # Create modulation from minor to major in 7 and 8
    
    eg_modulate_to_major = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'modulate', 
            from_bar = bar_prev, to_bar = bar_after, nr_generations = modulate_nr_generations)

    print(f"Generating evolutionary part {nr_current_generated} of {total_nr_evolutionary_parts}")
    nr_current_generated += 1
    eg_modulate_to_major.run_evolution()
    modulate_back_first_voice = copy.deepcopy(eg_modulate_to_major.best_individual)

    # Generate second voice as harmony to the first voice in bar 7 and 8
    
    eg_second_voice_modulate_back = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'harmony', 
            input_melody = modulate_first_voice, nr_generations = harmony_nr_generations)
    
    print(f"Generating evolutionary part {nr_current_generated} of {total_nr_evolutionary_parts}")
    nr_current_generated += 1
    eg_second_voice_modulate_back.run_evolution()    
    modulate_back_second_voice = copy.deepcopy(eg_second_voice_modulate.best_individual)
    
    
    # Add bar 7-10 to the voice tracks
    Track_Functions.add_tracks(first_voice, modulate_back_first_voice)
    Track_Functions.add_tracks(second_voice, modulate_back_second_voice)
    
    Track_Functions.add_tracks(first_voice, canon_first_voice)
    Track_Functions.add_tracks(second_voice, canon_second_voice)

    # Add cadence ending to second voice
    Track_Functions.second_voice_ending(second_voice, key)

    second_voice_ending = Track().add_bar(copy.deepcopy(second_voice[-3]))
    second_voice_ending.add_bar(copy.deepcopy(second_voice[-2]))
    
    # Generate harmony to cadence in first voice
    first_voice_last_bar = Track_Functions.first_voice_ending(first_voice, key)

    eg_first_voice_ending = EvolutionaryGenerator(key, nr_bars = 2, fitness_function = 'ending', 
            input_melody = second_voice_ending, from_bar = subject[0], to_bar = first_voice_last_bar[0], nr_generations = harmony_nr_generations)

    print(f"Generating evolutionary part {nr_current_generated} of {total_nr_evolutionary_parts}")
    eg_first_voice_ending.run_evolution()
    first_voice_ending = copy.deepcopy(eg_first_voice_ending.best_individual)
    Track_Functions.add_tracks(first_voice, first_voice_ending)
    Track_Functions.add_tracks(first_voice, first_voice_last_bar)

    #Add voices together to create a final composition
    fugue.add_track(first_voice)
    fugue.add_track(second_voice)

    #Generate lilypond file for fugue named final_fugue (removed for submission)
    finished_fugue = LilyPond.from_Composition(fugue)
    to_LilyPond_file(finished_fugue,"final_fugue")

    #Generate MIDI output for fugue named final_fugue
    midi_file_out.write_Composition("final_fugue.mid", fugue) 
    return

 
# Set number of generations to use for different types of generators
harmony_nr_generations = 200
modulate_nr_generations = 100
counter_nr_generations = 200

# Test for debugging
test_track, key = Track_Functions.init_preset_track("blinka")
generate_fugue(key, test_track)
#generate_longer_fugue(key, test_track, 3, ['Minor', 'Inverse', 'Reverse'])

