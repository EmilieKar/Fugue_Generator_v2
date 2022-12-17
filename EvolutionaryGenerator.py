import random as rnd
import numpy as np
import copy
import math
from mingus.core import *
from mingus.containers import *
import track_functions as Track_Functions
import fitness_functions as Fitness_Functions 

class EvolutionaryGenerator():

    def __init__(self, key, nr_bars = 2, fitness_function = 'C', global_max = None, input_melody = None, 
            from_bar = None, to_bar = None, from_key = None, to_key = None, wildness = False, nr_generations = 500):
        "Initialize all the parameters"
        
        # When testing to regenerate same case:
        #rnd.seed(1)
        #np.random.seed(1)

        # == Parameters ==
        self.fitness_function = fitness_function
        self.input_melody = input_melody
        self.from_bar = from_bar
        self.to_bar = to_bar
        self.from_key = from_key
        self.to_key = to_key
        
        self.population_size = 100
        self.nr_generations = nr_generations
        
        self.probability_rest = 0.05
        
        self.crossover_probability = 0.8;
        self.tournament_selection_parameter = 0.75;
        
        # Mutation probability different for different chromosomes, therefore decided in the mutate function.
        
        self.tournament_size = 2;
        self.nr_copies = 1;  
        
        self.pitch_probability = 0.5
        self.pause_probability = 0.5

        self.nr_bars = nr_bars
        self.key = key
        
        self.global_max = global_max
        self.best_individual = None
        self.max_fitness_value = 0
        
        self.wildness = wildness
        
        # Deciding here which note lengths that are allowed
        self.possible_lengths = [16, 8, 16/3, 4, 8/3, 2, 4/3, 1]

    def test_population(self):
        "Returns a population consisting of a single individual which is the C-scale."

        t = Track()
        bar = Bar(key = self.key)
        bar.place_notes('C', 4)
        bar.place_notes('D', 4)
        bar.place_notes('E', 4)
        bar.place_notes('F', 4)
        t.add_bar(bar)
        bar = Bar(key = self.key)
        bar.place_notes('G', 4)
        bar.place_notes('A', 4)
        bar.place_notes('B', 4)
        bar.place_notes('C', 4)
        t.add_bar(bar)
        
        self.population_size = 1
        
        return [t]
        
    def run_evolution(self):
        
        # Initialize population
        self.population = self.initialize_population()
        #self.population = self.test_population()
        
        fitness_values = np.zeros(self.population_size)
        self.max_fitness_value = -5000
        for iGen in range(self.nr_generations):
            
            # == Calculate fitness and save best individual ==
            fitness_values = self.calculate_fitness()
            
            # Save a copy of the best individual
            best_individual_index = np.argmax(fitness_values)        
            self.best_individual = copy.deepcopy(self.population[best_individual_index])
            
            # Print best individual and its fitness value if better than before
            if fitness_values[best_individual_index] > self.max_fitness_value:
                print(f"Generation: {iGen}")
                print(f"Best individual: {self.best_individual}")
                print(f"Maximal fitness: {fitness_values[best_individual_index]}")
                self.max_fitness_value = fitness_values[best_individual_index]
                if self.max_fitness_value == self.global_max:
                    break
            
            # == Tournament selection ==
            tmp_population = []
            for i in range(self.population_size):
                index_selected = self.tournament_selection(fitness_values, self.tournament_selection_parameter, self.tournament_size)
                individual_selected = copy.deepcopy(self.population[index_selected])
                tmp_population.append(individual_selected)
            
            
            # == Crossover ==
            for iCross in range(0, self.population_size-1, 2):
                chromosome1 = tmp_population[iCross]
                chromosome2 = tmp_population[iCross + 1]
                
                r_cross = rnd.random()
                if r_cross < self.crossover_probability:
                    crossed_pair = self.cross_over([chromosome1, chromosome2])
                    tmp_population[iCross] = crossed_pair[0]
                    tmp_population[iCross + 1] = crossed_pair[1]
                
            
            # == Mutation ==            
            for i in range(self.population_size):
                tmp_population[i] = self.mutate(tmp_population[i])
            
                        
            # == Elitism ==            
            tmp_population = self.insert_best_individual(tmp_population, self.best_individual)
            
            
            # == Save generation ==
            self.population = tmp_population
            
        
        # == Calculate fitness and save best individual ==
        fitness_values = self.calculate_fitness()
        
        # Save a copy of the best individual
        best_individual_index = np.argmax(fitness_values)        
        self.best_individual = copy.deepcopy(self.population[best_individual_index])
        
        # Print best individual and its fitness value if better than before
        if fitness_values[best_individual_index] > self.max_fitness_value:
            print(f"Generation: {iGen}")
            print(f"Best individual: {self.best_individual}")
            print(f"Maximal fitness: {fitness_values[best_individual_index]}")
            self.max_fitness_value = fitness_values[best_individual_index]
    
    def initialize_population(self, meter = (4,4), min_pitch = -12, max_pitch = 24):
        """Create the population consisting of the wanted number of
        randomly generated melodies.
        """
        population = []
        
        scale_tones = scales.get_notes(key = self.key)
        
        for i in range(self.population_size):
            melody = Track()            
            
            for i in range(self.nr_bars):
                bar = Bar(self.key, meter)
                while not bar.is_full():
                    # Decide length of a note. Maximum length is what is left of this bar.
                    length_left = 1 - bar.current_beat
                    
                    length = 0.5
                    while 1/length > length_left:
                        length = rnd.choice(self.possible_lengths)
                    
                    
                    # Decide pitch of a note                
                    r = rnd.random()
                    if r < self.probability_rest:
                        pitch_tone = None
                        # Add note to bar with the decided length                        
                        bar.place_rest(length)

                    else:
                        # Randomize a pitch
                        note_pitch = self.get_random_note_pitch(scale_tones)
                                            
                        # Add note to bar with the decided length                        
                        bar.place_notes(note_pitch, length)

                # Add note to subject
                melody.add_bar(bar)
                
            population.append(melody)
        
        return population

    def get_random_note_pitch(self, scale_tones):
        "Generates a note with random pitch"
        
        # Choose one random tone in the scale
        note_letter = rnd.choice(scale_tones)
        
        # Choose one random octave, with more chance to get close to 4.
        octave = 4 
        if self.wildness:
            octave = round(np.random.normal(loc = 4, scale = 0.5))
             
        # Note: Might be problematic if a octave number that is too high or too low is chosen.
        note = Note(note_letter, octave)
        
        return note
 
    def cross_over(self, chromosomes):
        """Change chromosome by using crossover between two chromosomes.
        It decides a beat to split and exchange tails after this beat
        between the two chromosomes.
        """
        
        # Decide at which semiquaver to cross
        bar_to_break_in = rnd.randrange(self.nr_bars)
        beat_to_break_at = rnd.randrange(16)/16
        
        
        # Initialize list to save heads and tails of each chromosome      
        head_chromosome = [Track(),Track()]
        tail_chromosome = [Track(),Track()]
        
        # Place to save the half bars that should be part of tail
        end_head_chromosome = [Bar(self.key), Bar(self.key)]
        start_tail_chromosome = [Bar(self.key), Bar(self.key)]
        
        for iChrom in range(2):
            
            bar_nr = 0
            for bar in chromosomes[iChrom]:
                # Bar before the break bar is added to head
                if bar_nr < bar_to_break_in:
                    head_chromosome[iChrom].add_bar(bar)
                
                # Bar after the break bar is added to tail
                elif bar_nr > bar_to_break_in:
                    tail_chromosome[iChrom].add_bar(bar)
                
                # The break bar is breaked in two parts.
                else:
                    # If breaking between bars, add the break bar to the tail
                    if beat_to_break_at == 0:
                        tail_chromosome[iChrom].add_bar(bar)
                        bar_nr += 1
                        continue
                    
                    beat = 0
                    note_index = 0
                    while beat < 1.0:
                        note_pitch = bar[note_index][2]
                        note_duration = bar[note_index][1]
                    
                        # If note stops before or at breakpoint, add to first part
                        if beat + 1/bar[note_index][1] <= beat_to_break_at:
                            end_head_chromosome[iChrom].place_notes(note_pitch, note_duration)
                        
                        # If note starts at or after breakpoint, add to second part
                        elif beat >= beat_to_break_at:
                            # If the first one after break, add it at the breakpoint. Otherwise, add it after the previous.
                            if beat == beat_to_break_at:
                                start_tail_chromosome[iChrom].current_beat = beat_to_break_at
                                
                            start_tail_chromosome[iChrom].place_notes(note_pitch, note_duration)
                        
                        else:  
                            # Divide to one part from beat to breakpoint, and one the length left over starting at breakpoint
                            first_part_duration = 1/(beat_to_break_at - beat)
                            second_part_duration = 1/(1/note_duration - 1/first_part_duration)
                            
                            end_head_chromosome[iChrom].place_notes(note_pitch, first_part_duration)
                            start_tail_chromosome[iChrom].current_beat = beat_to_break_at
                            start_tail_chromosome[iChrom].place_notes(note_pitch, second_part_duration)
                        beat += 1/bar[note_index][1]
                        note_index += 1
                        
                bar_nr += 1
        
        
        middle_bars = []
        cross_chromosomes = []
        for i in range(2):
        
            if beat_to_break_at != 0:
                # Combine the two middle parts in the new way
                middle_bars.append(self.combine_bars(end_head_chromosome[i], start_tail_chromosome[1-i]))
                
                # Add the changed middlebar to the head_chromosome
                head_chromosome[i].add_bar(middle_bars[i])
                
            # Create a new chromosome by adding the new tail to the head
            Track_Functions.add_tracks(head_chromosome[i], tail_chromosome[1-i])
            new_chromosome = head_chromosome[i]
        
            # Add the new chromosome to the list to be returned
            cross_chromosomes.append(new_chromosome)
        
        return cross_chromosomes

    def combine_bars(self, bar1, bar2):
    
        new_bar = Bar(self.key)
        end_bar1 = bar1.current_beat
        start_bar2 = bar2[0][0]
        
        if end_bar1 > start_bar2:
            raise ValueError('Bars overlapping.')
        
        if end_bar1 < start_bar2:
            # Fill the void with rests
            difference_duration = 1/(start_bar2 - end_bar1)
            bar1.place_rest(difference_duration)
            end_bar1 = bar1.current_beat
        
        if end_bar1 == start_bar2:
            for note in bar1:
                note_duration = note[1]
                note_type = note[2]
                
                if note_type is None:
                    new_bar.place_rest(note_duration)
                else:
                    new_bar.place_notes(note_type, note_duration)
                    
            for note in bar2:
                note_duration = note[1]
                note_type = note[2]
                
                if note_type is None:
                    new_bar.place_rest(note_duration)
                else:
                    new_bar.place_notes(note_type, note_duration)
        
        return new_bar

    def tournament_selection(self, fitness_values, 
            tournament_selection_parameter, tournament_size):
        "Select index of new individual by using tournament selection"
    
        # == Choose individuals for the tournament ==
        
        chosen_indices = [rnd.randrange(self.population_size) for i in range(tournament_size)]
        
        # == Sort chosen indices with highest fitness first ==
        
        chosen_fitness_values = [fitness_values[i] for i in chosen_indices] 

        value_and_index = [] 
          
        for i in range(len(chosen_fitness_values)): 
              value_and_index.append([chosen_fitness_values[i],chosen_indices[i]]) 
        value_and_index.sort() 
        sort_index = []
          
        for x in value_and_index: 
              sort_index.append(x[1]) 
          
        
        # == Run the tournament selection ==
        
        for i in range(tournament_size - 1):
            r = rnd.random()
            if r < tournament_selection_parameter:
                index_selected = sort_index[i]
                return index_selected
        index_selected = sort_index[-1]
        return index_selected

    def mutate(self, chromosome):
        """Mutate each gene with a certain probability. Can either split the note into two 
        notes of same pitch, shorten tone and add pause at the rest part or longer the note 
        and delete any notes that where there previously."""
        
        mutated_chromosome = Track()
        
        # Set key
        b = Bar(self.key)
        mutated_chromosome.add_bar(b)
        
        # Calculate number of notes in the chromosome
        nr_notes_in_chromosome = len([i for i in chromosome.get_notes()])
        
        # Decide mutation probability
        mutation_probability = 2/nr_notes_in_chromosome
        
        input_notes = chromosome.get_notes()
          
        notes_added = False
        ind = 0
        current_beat = 0
        for note in input_notes:
            ind += 1
            current_beat = (current_beat % 1)
            
            if current_beat == 0.0 and notes_added:
                if len(mutated_chromosome) == self.nr_bars:
                    break
                else:
                    current_beat += 1
            
            if not notes_added:
                notes_added = True
            
            note_beat = note[0]
            note_duration = note[1]
            note_pitch = note[2]

            # If completely covered by previous note, skip this note
            if note_beat < current_beat and note_beat != current_beat % 1:
                if note_beat + 1/note_duration <= current_beat:
                
                    continue
            
            # If the previous note is partly covered by previous note, add the not covered part
            if note_beat < current_beat and note_beat != current_beat % 1:
                new_note_duration = 1/(note_beat + 1/note_duration - current_beat)
                mutated_chromosome.add_notes(note_pitch, duration = new_note_duration)
                current_beat += 1/new_note_duration
                continue
            
            # If not affected by mutations on previous notes, check if this one should be mutated
                
            r = rnd.random()            
            if r < mutation_probability:
                # Mutate this note
                
                # Either change the pitch of the note                    
                r_pitch = rnd.random()
                if r_pitch < self.pitch_probability:
                
                    # Mutate the pitch
                    note_pitch = self.mutate_pitch(note_pitch)
                    
                    # Add mutated note to the mutated chromosome
                    mutated_chromosome.add_notes(note_pitch, note_duration)
                    current_beat += 1/note_duration
                
                # Or change the length of the note
                else:
                    
                    max_duration = 1/(1-(current_beat%1))
                    
                    # Mutate the duration
                    note_duration = self.mutate_duration(note_duration, max_duration)
                    
                    # Add mutated note to the mutated chromosome
                    mutated_chromosome.add_notes(note_pitch, note_duration[0])
                    current_beat += 1/note_duration[0]
                    
                    # If duration change is negative, fill up the empty space with note of
                    # same pitch or a rest.                    
                    if len(note_duration) > 1:
                        r_split = rnd.random()
                        if r_split < self.pause_probability:
                            mutated_chromosome.add_notes(note_pitch, note_duration[1])
                        else:
                            mutated_chromosome.add_notes(None, note_duration[1])
                        current_beat += 1/note_duration[1]
                        
                    continue
            # If no mutation, add the old note
            else:
                mutated_chromosome.add_notes(note_pitch, note_duration)
                current_beat += 1/note_duration
                        
        if len(mutated_chromosome) != self.nr_bars:
            # Some error must have occured
            raise ValueError('Number of bars has decreased.')
        
        return mutated_chromosome

    def mutate_pitch(self, note_pitch):

        # If the note was a rest
        if note_pitch is None:
            
            # Check which tones is in the scale
            scale_tones = scales.get_notes(self.key)
            
            # Generate a random pitch
            note_pitch = self.get_random_note_pitch(scale_tones)
            octave_change = None

        # If the note had a pitch, change it slightly
        else:
            # Decide change of pitch in halfnotes
            pitch_change = round(np.random.normal(scale = 4))
            octave_change = 0
            if abs(pitch_change) > 11:
                octave_change = pitch_change // 12
                pitch_change = pitch_change - 12*octave_change
                                
            interval_change = Track_Functions.get_interval_from_halfnotes(pitch_change)
            up = (pitch_change > 0)
            
            # Change the pitch (which is a NoteContainer)
            note_pitch = note_pitch.transpose(interval_change, up)
            for each_note_pitch in note_pitch:
                each_note_pitch.change_octave(octave_change)
                if len(each_note_pitch.name) > 2:
                    each_note_pitch = self.correct_accidentals(each_note_pitch)
        
        return note_pitch
            
    def mutate_duration(self, note_duration, max_duration):
        "Mutates the duration and returns list of new durations"
    
        durations = []
        for ind_max in range(len(self.possible_lengths)):
            if self.possible_lengths[ind_max] < max_duration:
                break
        
        
        # Decide how much to change the length
        new_note_duration = rnd.choice(self.possible_lengths[:ind_max])
        while 1/new_note_duration > 1/max_duration:
            new_note_duration = rnd.choice(self.possible_lengths)
            
        
        if new_note_duration < 0:
            breakpoint()
        durations.append(new_note_duration)
           
        length_change = 1/new_note_duration - 1/note_duration
           
        # If making the note shorter, fill up the space
        if length_change < 0:                    
            # Decide if the note should be split
            second_note_duration = -1/length_change
            durations.append(second_note_duration)
        
        return durations
    
    def calculate_fitness(self):
        "Calls on the wanted fitness function using self and the population as arguments."
        
        if self.fitness_function == 'C':
            fitness_values = Fitness_Functions.calculate_fitness_C(self.population)
            self.global_max = 2
        elif self.fitness_function == 'pauses':
            fitness_values = Fitness_Functions.calculate_fitness_rests(self.population)
        elif self.fitness_function == 'counter':
            fitness_values = Fitness_Functions.calculate_fitness_harmony(self.population, self.input_melody, self.key)
        elif self.fitness_function == 'modulate':
            fitness_values = Fitness_Functions.calculate_fitness_modulate(self.population, self.from_bar, self.to_bar)
        elif self.fitness_function == 'harmony':
            if len(self.input_melody) == 0:
                raise ValueError('Input is empty')
            fitness_values = Fitness_Functions.calculate_fitness_harmony(self.population, self.input_melody, self.key)
        elif self.fitness_function == 'ending':
            fitness_values = Fitness_Functions.calculate_fitness_harmony_and_modulate(self.population, self.from_bar, self.to_bar, self.input_melody, self.key)
        elif self.fitness_function == 'test':
            fitness_values = Fitness_Functions.calculate_fitness_test(self.population, self.input_melody, self.key)

        return fitness_values
   
    def insert_best_individual(self, tmp_population, best_individual):
        """Insert the individual with highest fitness in the previous
        generation to the new generation.
        """
        
        for i in range(self.nr_copies):
            tmp_population[i] = best_individual

        return tmp_population
    
    def correct_accidentals(self, pitch):
        "Change the note name to be as simple as possible"

        pitch.remove_redundant_accidentals()
        ind = 0
        while len(pitch.name) > 2:
            ind += 1
            if ind > 1:
                breakpoint()
            tone = pitch.name[0]
            if pitch.name[1] == 'b':
                if tone == 'C':
                    pitch.name = 'B' + pitch.name[1:]
                    pitch.name = pitch.name[:-1]
                elif tone == 'F':
                    pitch.name[0] = 'E'
                    pitch.name = pitch.name[:-1]
                else:
                    if tone == 'D':
                        pitch.name = 'C' + pitch.name[1:]
                    elif tone == 'E':
                        pitch.name = 'D' + pitch.name[1:]
                        
                    elif tone == 'G':
                        pitch.name = 'F' + pitch.name[1:]
                    elif tone == 'A':
                        pitch.name = 'G' + pitch.name[1:]
                    elif tone == 'B':
                        pitch.name = 'A' + pitch.name[1:]
                    pitch.name = pitch.name[:-2]
            else:
                if tone == 'B':
                    pitch.name = 'C' + pitch.name[1:]
                    pitch.name = pitch.name[:-1]
                elif tone == 'E':
                    pitch.name = 'F' + pitch.name[1:]
                    pitch.name = pitch.name[:-1]
                else:
                    if tone == 'C':
                        pitch.name = 'D' + pitch.name[1:]
                    elif tone == 'D':
                        pitch.name = 'E' + pitch.name[1:]
                        
                    elif tone == 'F':
                        pitch.name = 'G' + pitch.name[1:]
                    elif tone == 'G':
                        pitch.name = 'A' + pitch.name[1:]
                    elif tone == 'A':
                        pitch.name = 'B' + pitch.name[1:]
                    pitch.name = pitch.name[:-2]
                            
        return pitch
                    