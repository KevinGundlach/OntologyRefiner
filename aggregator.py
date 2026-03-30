from typing import List, Tuple, Dict

class DataAggregator:

    def __init__(self):
        self.entries : List[Tuple[str, str]] = []


    def insert(
            self, 
            entry_or_group : Tuple[str, str]
                           | List[Tuple[str, str]]
                           | Dict[str, str]
                           | List[Dict[str, str]]
        ):

        # The critic outputs its proposed variables as lists of dictionaries,
        # since it can output different variables with duplicate names 
        # but different definitions. The consolidator's job is to handle that.
        
        # This aggregator stores the proposed variables as a list of (key, value) pairs. 

        # The ontology.py stores the data extractor's variables in a plain dictionary.

        # This insert function is designed to recognize any such format.

        if type(entry_or_group) is tuple or type(entry_or_group) is dict:
            self._insert_entry(entry_or_group)

        elif type(entry_or_group) is list:            
            for entry in entry_or_group:
                self._insert_entry(entry)

        else:
            raise ValueError(f"Unrecognized group type: {type(entry_or_group)}.")


    def _insert_entry(self, entry : Tuple[str, str] | Dict[str, str]):
        if type(entry) is tuple:
            self.entries.append(entry)
        elif type(entry) is dict:
            self.entries.extend(entry.items()) 
        else:
            raise ValueError(f"Unrecognized entry type: {type(entry)}.")

    def get_normalized_entry_counts(
            self, 
            normalizing_map : Dict[str, str] | List[Dict[str, str]],
            exceptions : List[str]
        ):

        # Main purpose is to count the number of times the critic proposed
        # a particular variable, *not* counting those that are already
        # defined in ontology.py.

        # The consolidator outputs the normalizing map as a list of dictionaries
        # to match its input, though I'll probably change that.

        if type(normalizing_map) is list:
            normalizing_map = dict([list(d.items())[0] for d in normalizing_map])

        normalized_exceptions = [normalizing_map[e] for e in exceptions]
        counts = {}

        for (name, definition) in self.entries:

            normalized_name = normalizing_map[name]
            
            if normalized_name in normalized_exceptions:
                continue

            if normalized_name in counts:
                counts[normalized_name] += 1
            else:
                counts[normalized_name] = 1

        return counts
