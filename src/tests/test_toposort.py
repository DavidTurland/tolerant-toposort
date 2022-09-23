import concurrent.futures

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

class Testfunctional(TestCase):
    def test_processed_removal(self):
        batches   = [{7,5},{3, 5, 7}, {8, 10, 11}, {9, 2, 12}]
        processed = {7,5}
        expected  = [{3}, {8, 10, 11}, {9, 2, 12}]

        output_list = list(filter(None,(batch - processed for batch in batches)))

        self.assertListEqual(output_list,expected)


class TestConcurrentProcess(TestCase):
    """ Slightly more representative test cases
- disabled nodes are only discovered whilst being processed
- processed nodes are cached
- processed nodes are not processed again
NOTE: All nodes in a batch can be processed concurrently, obviously...
    
"""
    willBeDisabled = {7}

    def process_node(self,node,processed):
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
        processed      = {} # persist this!!
        while True:
            batches = toposort(graph,disabled)
            # we may have processed nodes from an earlier invocation of toposort
            # so remove all processed nodes from batches, and remove empty batches
            batches = list(filter(None,(batch - processed.keys() for batch in batches)))

            processedAny = False
            if not batches:
                break
            try:
                for batch in batches:
                    disabledThisBatch = set()
                    with concurrent.futures.ThreadPoolExecutor(max_workers = len(batch)) as executor:
                        future_to_node = {executor.submit(self.process_node, node, processed): node for node in batch}
                        for future in concurrent.futures.as_completed(future_to_node):
                            node    = future_to_node[future]
                            success = future.result()
                            processed[node] = success
                            processedAny = True
                            if not success:
                                disabledThisBatch.add(node)                              
                    if disabledThisBatch: 
                        raise ProcessException(disabledThisBatch)
                if not processedAny:
                    break
            except ProcessException as be:
                disabled.update(be.nodes)

        self.assertSetEqual(disabled,self.willBeDisabled)

        expectedProcessed= {3 : True, 
                            5 : True, 
                            7 : False, 
                            10: True, 
                            12: True}
        self.assertDictEqual(processed,expectedProcessed)





