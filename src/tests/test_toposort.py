from unittest import TestCase

from tolerant.toposort import toposort,CircularDependencyError

class TestVanilla(TestCase):
    def test_tiny(self):
        actual = list(toposort({1: {2},
                                2: {3},
                                3: {4},
                           }))
        expected = [{4}, {3}, {2}, {1}]
        self.assertListEqual(actual,expected)

    def test_small(self):
        actual = list(toposort({2: {2,11},
                                9: {11, 8, 10},
                               10: {3},
                               11: {7, 5},
                                8: {7, 3},
                               12: {10},
               }))
        expected = [{3, 5, 7}, {8, 10, 11}, {9, 2, 12}]
        self.assertListEqual(actual,expected)

    def test_circular(self):
        with self.assertRaises(CircularDependencyError):
            x = list(toposort({1: {2},
                               2: {3},
                               3: {4},
                               4: {1},
                               6: {7},
                              }))

class TestTolerant(TestCase):
    def test_tiny_one_disabled(self):
        actual = list(toposort({1: {2},
                                2: {3},
                                3: {4},
                           },{3}))
        expected = [{4}]
        self.assertListEqual(actual,expected)

    def test_small_one_disabled(self):
        actual = list(toposort({2: {2,11},
                                9: {11, 8, 10},
                               10: {3},
                               11: {7, 5},
                                8: {7, 3},
                               12: {10},
                               },{7}))
        expected = [{3, 5}, {10}, {12}]
        self.assertListEqual(actual,expected)

    def test_circular(self):
        with self.assertRaises(CircularDependencyError):
            x = list(toposort({1: {2},
                               2: {3},
                               3: {4},
                               4: {1},
                               6: {7},
                              }))
    def test_circular_two(self):
        with self.assertRaises(CircularDependencyError):
            x = list(toposort({1: {2},
                               2: {3},
                               3: {4},
                               4: {1},
                               6: set(),
                              },{6}))

class ProcessException(ValueError):
    def __init__(self, nodes):
        self.nodes = nodes

class TestProcess(TestCase):
    """ Slightly more representative test cases
disabled nodes are only discovered whilst being processed
All nodes in a batch can be attempted to be processed, just accrue the disabled
    
"""
    willBeDisabled = {7}

    def process(self,node):
        return node not in self.willBeDisabled

    def test_process_small_one_disabled(self):
        graph = {2: {2,11},
                 9: {11, 8, 10},
                10: {3},
                11: {7, 5},
                 8: {7, 3},
                12: {10},
                }
        willBeDisabled = {7}
        disabled       = set()
        processed      = set() # persist this!!
        while True:
            batches = toposort(graph,disabled)
            processedAny = False
            if not batches:
                break
            try:
                for batch in batches:
                    disabledThisBatch = set()
                    # add concurrency ( and mutexes around shared variables)
                    for node in batch:
                        if node in processed:
                            continue
                        if self.process(node):
                            processed.add(node)
                            processedAny= True
                        else:
                            disabledThisBatch.add(node)
                    if disabledThisBatch: 
                        raise ProcessException(disabledThisBatch)
                if not processedAny:
                    break
            except ProcessException as be:
                disabled.update(be.nodes)

        self.assertSetEqual(disabled,self.willBeDisabled)

        expectedProcessed= {10,3,12,5}
        self.assertSetEqual(processed,expectedProcessed)





