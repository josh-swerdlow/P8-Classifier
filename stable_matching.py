import sys
import numpy as np

class PreferenceMatrix():
    """
    Summary: ??? This is pretty broken at the moment

    Attributes:
        preferences: A python dictionary of ElementArray objects containing the preferences

    """
    def __init__(self, keys, prefs):

        # Check that keys is the correct instance
        if not isinstance(keys, ElementArray):
            sys.exit('PreferenceMatrix Error: keys must be an ElementArray')

        # Check the lengths of the keys and preferences
        if len(keys.values) != len(prefs):
            sys.exit('PreferenceMatrix Error: keys and prefs must be same length')
        else:
            number_preferences = len(keys.values)

        self.preferences = dict()

        # Add all the keys and preferences into the appropriate
        # bins of the dictionary
        for pref_idx, key in enumerate(keys.values):
            pref = ElementArray(prefs[pref_idx])

            self.preferences[key] = pref

            # print('preferences[{}] = {}'.format(key.value, [element.value for element in pref.values]))
            # print('proposed = {}'.format(pref.proposed))

class Matches():
    """
        Summary: This is the workhorse of the stable matching algorithm. This stores all the pairs found
                    during the algorithms run by using internal match and unmatch functions.

        Attributes:
            pairs: A list of pairs (proposer, acceptor) containing a tuple of Element objects.

    """
    def __init__(self):
        self.pairs = list()

    # Match the two elements to one another if they have not already been matched
    def match(self, proposer, acceptor):
        # Check if the pair is already in the list of matches
        if proposer.matched or acceptor.matched:
            print('match error: {} or {} is already matched.'.format(proposer.value, acceptor.value))
            return -1
        else:
            proposer.matched = True
            acceptor.matched = True

            pair = (proposer, acceptor)
            self.pairs.append(pair)
            # print('Matching ({}, {})'.format(pair[0].value, pair[1].value))

    # Unmatch the proposer and acceptor from one another if they are both matched
    # Problem: This doesn't check if they are necessarily matched together
    def unmatch(self, proposer, acceptor):

        if not (proposer.matched and acceptor.matched):
            print('unmatch error: {} or {} is not matched.'.format(proposer.value, acceptor.value))
            return -1
        else:
            proposer.matched = False
            acceptor.matched = False

            pair = (proposer, acceptor)
            self.pairs.remove(pair)

class ElementArray():
    """
        Summary: An object to store a list of Element object and hold the index of the most recently
                    proposed to Element in the ElementArray.


        Attributes:
            elements: A one dimensional list of Element objects
            proposed: An integer value to represent the index of last Element in the elements list
                        which was proposed to.
    """
    def __init__(self, elements):

        # Check to ensure the elements argument is a numpy array or list (which gets turned into a numpy array)
        if not isinstance(elements, np.ndarray):
            if isinstance(elements, list):
                elements = np.array(elements)
            else:
                sys.exit('ElementArray Error: elements must be array like.')

        # Initialize the elements list
        self.elements = list()
        for value in elements:
            self.elements.append(Element(value))

        # Intialize the proposed value
        self.proposed = 0

class Element():
    """
        Description: This is a single component of a large object with stores multiple
        data element to be matched together via preferences using the Gale-Shapely
        stable matching algorithm.

        Attributes:
            value: The value of the element, can be string, int, float, etc
            matched [False]: A boolean value to indicate if the element has been matched
    """
    def __init__(self, value):
        self.value = value
        self.matched = False