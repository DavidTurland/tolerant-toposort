#######################################################################
# Tests for tolerant.toposort module.
# Copyright David Turland 2023
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Notes:
#
# The tests:
#
# TestVanilla - The inherited functionality from Original Toposort:
#
# TestTolerant - The new functionality supporting disabled nodes 
#
# TestProcess - A simple use-case
#   A tree of elements are repeatedly processed until no more can be done
#   One of the element will 'fail' to be processed
#   on failure a new toposort is calculated
#   successfully processed nodes are not re-processed
#
# TestConcurrentProcess A Slightly less simple use-case
#   A tree of elements are repeatedly processed until no more can be done
#   Elements in a barch are processed concurrently
#   One of the element will 'fail' to be processed
#   on failure a new toposort is calculated
#   successfully processed nodes are not re-processed
#
########################################################################

import concurrent.futures

from unittest import TestCase

from tolerant.toposort import toposort,toposort_flatten,CircularDependencyError

class TestPython101(TestCase):
    def test_objects(self):
        o2  = object()
        o3  = object()
        o5  = object()
        o7  = object()
        o8  = object()
        o9  = object()
        o10 = object()
        o11 = object()
        data = {
                o2: {o11},
                o9: {o11, o8},
                o10: {o11, o3},
                o11: {o7, o5},
                o8: {o7, o3, o8},
            }
        # same key objects, new item(set) object with same items (less any self-reference)
        # this is fine...
        _data = {item: set(e for e in dep if e != item) for item, dep in data.items()}

        for k, v in data.items():
           for i in v:
              self.assertIn(k,_data)
              if i is k:
                 continue
              self.assertIn(i,_data[k])

class TestVanilla(TestCase):
    """ 
    The inherited functionality from Original Toposort
    """
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
    def test_input_modified_to_remove_self_references(self):
        """
          Changes to original toposort:
            The input will have its self-referential elements removed
            Test renamed from 'test_input_not_modified'
        """
        def get_data():
            return {
                2: {11},
                9: {11, 8},
                10: {11, 3},
                11: {7, 5},
                8: {7, 3, 8},  # Includes something self-referential.
            }

        data = get_data()
        orig = get_data()
        self.assertEqual(data, orig)
        results = list(toposort(data))
        self.assertEqual(data, orig,"self-reference Not removed")

        # we need to remove the self-reference
        #orig[8].remove(8)
        # and then it matches
        self.assertEqual(data, orig)
        expected = [{3, 5, 7}, {8, 11}, {9, 2, 10}]
        self.assertEqual(results, expected)

class TestTolerant(TestCase):
    """ 
    The new functionality supporting disabled nodes 
    """
    def test_tiny_one_disabled(self):
        actual = list(toposort({1: {2},
                                2: {3},
                                3: {4},
                           },{3}))
        expected = [{4}]
        self.assertListEqual(actual,expected)

    def test_tiny_all_disabled(self):
        actual = list(toposort({1: {2},
                                2: {3},
                                3: {4},
                                },{1,2,3,4}))
        expected = []
        self.assertListEqual(actual,expected)

    def test_tiny_more_than_all_disabled(self):
        actual = list(toposort({1: {2},
                                2: {3},
                                3: {4},
                               },{1,2,3,4,5}))
        expected = []
        self.assertListEqual(actual,expected) 

    def test_doc_sample(self):
        data = {
            2:  {11},
            9:  {11, 8},
            10: {11, 3},
            11: {7, 5},
            8:  {7, 3},
        }
        disabled = {5}
        actual = list(toposort(data,disabled))
        expected = [{3, 7}, {8}]
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
                              
    def test_sort_flatten(self):
        data = {
            2:  {11},
            9:  {11, 8},
            10: {11, 3},
            11: {7, 5},
            8:  {7, 3, 8},  # Includes something self-referential.
        }
        # No dependants, so just this item will be removed from batches
        disabled = {10}
        expected = [{3, 5, 7}, {8,11},{2,9}]
        result = list(toposort(data,disabled))
        self.assertEqual(result, expected)

        # Now check the sorted results.
        expected_results = []
        for item in expected:
            expected_results.extend(sorted(item))

        result = toposort_flatten(data, True,disabled)
        self.assertEqual(result, expected_results)

        # And the unsorted results.  Break the results up into groups to
        # compare them.
        actual = toposort_flatten(data, False,disabled)

        results = [
            {i for i in actual[0:3]},
            {i for i in actual[3:5]},
            {i for i in actual[5:8]},
        ]
        self.assertEqual(results, expected)
        
class ProcessException(ValueError):
    def __init__(self, nodes):
        self.nodes = nodes

class TestProcess(TestCase):
    """ Slightly more representative test cases
    disabled nodes are only discovered whilst being processed
    All nodes in a batch can be attempted to be processed, just accrue the disabled
    """
    willBeDisabled = {7}
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def shortDescription(self):
        return "Slightly more representative test cases"

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

        disabled       = set() # In real-life this will be persisted !!
        processed      = set() # In real-life this will be persisted !!
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
    """ Even more representative test cases
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

        disabled       = set() # In real-life this will be persisted !!
        processed      = {} # In real-life this will be persisted !!
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


