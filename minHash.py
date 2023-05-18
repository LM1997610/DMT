
import csv
from tqdm import tqdm
import random
import numpy as np
import itertools as it

max_shingle_id = 0
map__shingle__shingle_id = {}

class Shingling:

    def cleaner(self, text, set__characters_of_interest):
        new_text = ""
        #
        previous_copied_character = "a"
        for c_character in text:
            #
            c_character = c_character.lower()
            #
            if c_character not in set__characters_of_interest:
                c_character = " "
            #
            if c_character == " " and c_character == previous_copied_character:
                continue
            #
            new_text += c_character
            #
            previous_copied_character = c_character
            #
        #
        new_text = new_text.strip()
        #
        return new_text

    def get_shingle_id(self, shingle):

        global max_shingle_id
        global map__shingle__shingle_id
        #
        shingle_id = map__shingle__shingle_id.get(shingle, -1)
        #
        if shingle_id >= 0:
            return shingle_id
        #
        max_shingle_id += 1
        shingle_id = max_shingle_id
        map__shingle__shingle_id[shingle] = max_shingle_id
        #
        return shingle_id
    
    def shingler(self, text, width=2):
        #
        set__shingle_id = set()
        #
        tokenized_text = text.split(" ")
        #
        max_index_plus_1 = 1 if len(tokenized_text) <= width else len(tokenized_text) - width +1
        for index in range(max_index_plus_1):
            #
            c_shingle = tuple(tokenized_text[index:index + width])
            #
            shingle_id = Shingling.get_shingle_id(self, c_shingle)
            #
            # if shingle_id in set__shingle_id:
            #    print(shingle_id, c_shingle)
            #
            res = set__shingle_id.add(shingle_id)
            #
        return set__shingle_id
    
    def create_sets_of_shingle_ids(self, input_file_name, output_file_name,
                               input_file_delimiter='\t', input_file_quotechar='"',
                               set__characters_of_interest=[" "], shingle_width=3,
                               doc_id_column_idx=0, field_column_idx=1):
        #
        output_file = open(output_file_name, 'w', encoding="utf-8")
        output_file_csv_writer = csv.writer(output_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
        header = ['set_id', 'set_of_integers']
        output_file_csv_writer.writerow(header)
        #
        input_file = open(input_file_name, 'r', encoding="utf-8")
        input_file_csv_reader = csv.reader(input_file, delimiter=input_file_delimiter, quotechar=input_file_quotechar)
        next(input_file_csv_reader)
        input_file_csv_reader = [x for x in input_file_csv_reader]
        for record in tqdm(input_file_csv_reader): # total = 150000):
            #
            doc_id = int(record[doc_id_column_idx])
            document = record[field_column_idx]
            #
            cleaned_document = Shingling.cleaner(self, document, set__characters_of_interest)
            #
            set__shingle_id = Shingling.shingler(self, cleaned_document, width=shingle_width)
            #
            output_file_csv_writer.writerow([doc_id, set__shingle_id])
            #
            #
            #if doc_id % 1000 == 0:
            #    print("Last processed doc_id:", doc_id)
            #
        input_file.close()
        output_file.close()
        print("Last processed doc_id:", doc_id)
        print()
        print(" max_shingle_id =", max_shingle_id)
        print()
        print()
        return max_shingle_id


class MinWiseHashing:

    def is_prime(self, number):
    
        if number == 2:
            return True
        if (number % 2) == 0:
            return False
        for j in range(3, int(number ** 0.5 + 1), 2):
            if (number % j) == 0:
                return False
        #
        return True
    
    def create_hash_functions(self, number_of_hash_functions, upper_bound_on_number_of_distinct_elements, seed=42):
        random.seed(seed)
        #
        map__hash_function_id__a_b_p = {}
        #
        set_of_all_hash_functions = set()
        while len(set_of_all_hash_functions) < number_of_hash_functions:
            a = random.randint(1, upper_bound_on_number_of_distinct_elements - 1)
            b = random.randint(0, upper_bound_on_number_of_distinct_elements - 1)
            p = random.randint(upper_bound_on_number_of_distinct_elements, 10 * upper_bound_on_number_of_distinct_elements)
            while MinWiseHashing.is_prime(self, p) == False:
                p = random.randint(upper_bound_on_number_of_distinct_elements,
                                10 * upper_bound_on_number_of_distinct_elements)
            #
            c_hash_function = (a, b, p)
            set_of_all_hash_functions.add(c_hash_function)
        #
        for c_hash_function_id, c_hash_function in enumerate(set_of_all_hash_functions):
            map__hash_function_id__a_b_p[c_hash_function_id] = c_hash_function
        #
        return map__hash_function_id__a_b_p
    
    def create_c_set_MinWiseHashing_sketch(self, c_set,
                                       map_as_list__index__a_b_p,
                                       total_number_of_hash_functions, use_numpy_version = True):
        if use_numpy_version:
            app = np.array(map_as_list__index__a_b_p)
            c_set_MinWiseHashing_sketch = list(np.min((app[:,:1]*np.array(list(c_set))[None,:]+app[:,1:2])%app[:,2:],axis=1))
        else:
            plus_inf = float("+inf")
            c_set_MinWiseHashing_sketch = [plus_inf] * total_number_of_hash_functions
            for c_element_id in c_set:
                for index, (a, b, p) in enumerate(map_as_list__index__a_b_p):
                    c_hash_value = (a * c_element_id + b) % p
                    if c_hash_value < c_set_MinWiseHashing_sketch[index]:
                        c_set_MinWiseHashing_sketch[index] = c_hash_value
                #
            #   
        #
        return c_set_MinWiseHashing_sketch

    def create_MinWiseHashing_sketches(self, input_file_name, upper_bound_on_number_of_distinct_elements,
                                   number_of_hash_functions_that_is_also_the_sketch_lenght_and_also_the_number_of_simulated_permutations,
                                   output_file_name, use_numpy_version=True):
    #
        map__hash_function_id__a_b_p = MinWiseHashing.create_hash_functions(self,  
                number_of_hash_functions_that_is_also_the_sketch_lenght_and_also_the_number_of_simulated_permutations,
                upper_bound_on_number_of_distinct_elements)
        #
        map__set_id__MinWiseHashing_sketch = {}
        #
        total_number_of_hash_functions = len(map__hash_function_id__a_b_p)
        # sorted_list_all_hash_function_id = sorted(map__hash_function_id__a_b_p.keys())
        map_as_list__index__a_b_p = tuple([(a, b, p) for a, b, p in map__hash_function_id__a_b_p.values()])
        #
        input_file = open(input_file_name, 'r', encoding="utf-8")
        input_file_csv_reader = csv.reader(input_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
        header = next(input_file_csv_reader)
        input_file_csv_reader = [x for x in input_file_csv_reader if len(x) != 0]
        num_record_so_far = 0

        for record in tqdm(input_file_csv_reader): #, total = 300001):
            
            num_record_so_far += 1
            #if num_record_so_far % 100 == 0:
                #print(num_record_so_far)

            c_set_id = int(record[0])
            c_set = eval(record[1])

            c_set_MinWiseHashing_sketch = MinWiseHashing.create_c_set_MinWiseHashing_sketch(self, c_set,map_as_list__index__a_b_p,
                                                                            total_number_of_hash_functions,
                                                                            use_numpy_version)
            
            #print(len(c_set_MinWiseHashing_sketch))
            map__set_id__MinWiseHashing_sketch[c_set_id] = c_set_MinWiseHashing_sketch
        input_file.close()
        #
        output_file = open(output_file_name, 'w', encoding="utf-8")
        output_file_csv_writer = csv.writer(output_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
        #header = ['set_id', 'MinWiseHashing_sketch']
        output_file_csv_writer.writerow(header)
        sorted_list_all_set_id = sorted(map__set_id__MinWiseHashing_sketch.keys())
        for c_set_id in sorted_list_all_set_id:
            output_file_csv_writer.writerow([c_set_id, str(map__set_id__MinWiseHashing_sketch[c_set_id])])
        output_file.close()
        #
        return
    

class LSH:

    def load_map__set_id__MinWiseHashing_sketch_from_file(self, input_file_name):
        map__set_id__MinWiseHashing_sketch = {}
        #
        input_file = open(input_file_name, 'r', encoding="utf-8")
        input_file_csv_reader = csv.reader(input_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
        header = next(input_file_csv_reader)
        for record in tqdm(input_file_csv_reader, total =300002/2) :
            if len(record) != 0:
                c_set_id = int(record[0])
                c_MinhiseHashing_sketch = tuple(eval(record[1]))
            #
                map__set_id__MinWiseHashing_sketch[c_set_id] = c_MinhiseHashing_sketch
            #
        input_file.close()
        #
        return map__set_id__MinWiseHashing_sketch
    
    def get_set_of_CANDIDATES_to_be_near_duplicates(self, r, b, map__set_id__MinWiseHashing_sketch):
        #
        set_of_CANDIDATES_to_be_near_duplicates = set()
        #
        for c_band_progressive_id in tqdm(range(b)):
            #
            #print("c_band_progressive_id", c_band_progressive_id)
            #
            c_band_starting_index = c_band_progressive_id * r
            c_band_ending_index = (c_band_progressive_id + 1) * r
            #
            map__band__set_set_id = {}
            #
            for c_set_id in map__set_id__MinWiseHashing_sketch:
                #
                if r * b != len(map__set_id__MinWiseHashing_sketch[c_set_id]):
                    n = len(map__set_id__MinWiseHashing_sketch[c_set_id])
                    message = "ERROR!!! n != r*b " + str(n) + "!=" + str(r * b) + "; " + str(n) + "!=" + str(r) + "*" + str(
                        b)
                    raise ValueError(message)
                #
                c_band_for_c_set = tuple(
                    map__set_id__MinWiseHashing_sketch[c_set_id][c_band_starting_index:c_band_ending_index])
                #
                if c_band_for_c_set not in map__band__set_set_id:
                    map__band__set_set_id[c_band_for_c_set] = set()
                map__band__set_set_id[c_band_for_c_set].add(c_set_id)
                #

            for c_set_set_id in map__band__set_set_id.values():
                #
                if len(c_set_set_id) > 1:
                    #
                    for set_id_a, set_id_A in it.combinations(c_set_set_id, 2):
                        if set_id_a < set_id_A:
                            set_of_CANDIDATES_to_be_near_duplicates.add((set_id_a, set_id_A))
                        else:
                            set_of_CANDIDATES_to_be_near_duplicates.add((set_id_A, set_id_a))
            #
        #
        return set_of_CANDIDATES_to_be_near_duplicates

    def compute_approximate_jaccard(self, set_a_MinWiseHashing_sketch, set_b_MinWiseHashing_sketch):
        appx_jaccard = 0.
        #
        for index in range(len(set_a_MinWiseHashing_sketch)):
            #
            if set_a_MinWiseHashing_sketch[index] == set_b_MinWiseHashing_sketch[index]:
                appx_jaccard += 1
            #
        appx_jaccard /= len(set_a_MinWiseHashing_sketch)
        #
        return appx_jaccard

    def compute_approximate_jaccard_to_REDUCE_the_number_of_CANDIDATES_to_be_near_duplicates(self, 
        set_of_CANDIDATES_to_be_near_duplicates, map__set_id__MinWiseHashing_sketch, jaccard_threshold):

        map__set_a_id__set_A_id__appx_jaccard = {}
        #
        for set_a_id, set_A_id in set_of_CANDIDATES_to_be_near_duplicates:
            #
            set_a_MinWiseHashing_sketch = map__set_id__MinWiseHashing_sketch[set_a_id]
            set_A_MinWiseHashing_sketch = map__set_id__MinWiseHashing_sketch[set_A_id]
            #
            appx_jaccard = LSH.compute_approximate_jaccard(self, set_a_MinWiseHashing_sketch, set_A_MinWiseHashing_sketch)
            #
            if appx_jaccard >= jaccard_threshold:
                map__set_a_id__set_A_id__appx_jaccard[(set_a_id, set_A_id)] = appx_jaccard
            #
        #
        return map__set_a_id__set_A_id__appx_jaccard
    
    def mine_couples_of_Near_Duplicates(self, input_file_name, output_file_name, r, b, jaccard_threshold):
    #
        print("Starting the loading of the MinWiseHashing sketches from the input file.")
        map__set_id__MinWiseHashing_sketch = LSH.load_map__set_id__MinWiseHashing_sketch_from_file(self, input_file_name)
        print()
        print("Number of sets =", len(map__set_id__MinWiseHashing_sketch))
        print()
        #
        print("Starting the mining of the CANDIDATES couples to be near duplicates.")
        set_of_CANDIDATES_to_be_near_duplicates = LSH.get_set_of_CANDIDATES_to_be_near_duplicates(self, r, b,
                                                                                            map__set_id__MinWiseHashing_sketch)
        #
        print()
        print("Number of pairs of sets to be near-duplicate CANDIDATES =", len(set_of_CANDIDATES_to_be_near_duplicates))
        print()
        #
        map__set_a_id__set_A_id__appx_jaccard = LSH.compute_approximate_jaccard_to_REDUCE_the_number_of_CANDIDATES_to_be_near_duplicates(
            self, set_of_CANDIDATES_to_be_near_duplicates, map__set_id__MinWiseHashing_sketch, jaccard_threshold)
        print()
        print("Number of REFINED pairs of sets to be near-duplicate CANDIDATES =",
            len(map__set_a_id__set_A_id__appx_jaccard))
        print()

        print()
        print("FALSI POSITIVI = ",len(set_of_CANDIDATES_to_be_near_duplicates) -
            len(map__set_a_id__set_A_id__appx_jaccard))
        print()
        #
        output_file = open(output_file_name, 'w', encoding="utf-8")
        output_file_csv_writer = csv.writer(output_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_NONE)
        header = ['set_a_id', 'set_b_id', 'approximate_jaccard']
        output_file_csv_writer.writerow(header)
        sorted_list_all_set_id = sorted(map__set_id__MinWiseHashing_sketch.keys())
        for set_a_id__set_A_id in map__set_a_id__set_A_id__appx_jaccard:
            appx_jaccard = map__set_a_id__set_A_id__appx_jaccard[set_a_id__set_A_id]
            output_file_csv_writer.writerow([set_a_id__set_A_id[0], set_a_id__set_A_id[1], appx_jaccard])
        output_file.close()
        return





