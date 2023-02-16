#######################################################################
# Implements a topological sort algorithm.
# Copyright David Turland 2023
# Copyright 2014 True Blade Systems, Inc.
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
#  Based on https://pypi.org/project/toposort
#  with these changes:
#  -   toposort and toposort_flatten take an optional set of disabled items.
#      These disabled items, and their dependents, will not be included
#      in the returned batch(es)
#
########################################################################
""" Generates successive batches of dependant items which are enabled and do not depend
    on disabled items

Based on [toposort](https://pypi.org/project/toposort)
with these changes:
-   **toposort** and **toposort_flatten** take an optional set of disabled items.
    These disabled items, and their dependents, will not be included
    in the returned batch(es)
"""
from functools import reduce as _reduce
#import copy
__all__ = ['toposort', 'toposort_flatten', 'CircularDependencyError']


class CircularDependencyError(ValueError):
    """ An item _eventually_ depends on itself

        **NOTE** : we tolerate items _directly_ depending on themeselves
    """
    def __init__(self, data):
        """ ## Args
	  - **data** : the list containing  the circular dependency
        """
        # Sort the data just to make the output consistent, for use in
        #  error messages.  That's convenient for doctests.
        s = "Circular dependencies exist among these items: {{{}}}".format(
            ", ".join(
                "{!r}:{!r}".format(key, value) for key, value in data.items()
            )
        )
        super(CircularDependencyError, self).__init__(s)
        self.data = data


def toposort(data, disabled = set()):
    """\
Dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items.  
Returns a list of sets in topological order. The first set consists of items with no
dependences, each subsequent set consists of items that depend upon
items in the preceeding sets.

## Args
- **data** - the dependency graph
dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items. 

- **disabled**(optional) - Set of items which, with their dependents, should not be
  included in the output

## Returns
- a list of sets in topological order which are not disabled, or depend on
a disabled item.  
The first set consists of items with no dependences, each subsequent set 
consists of items that depend upon items in the preceeding sets.
"""

    # Special case empty input.
    if len(data) == 0:
        return

    ##_data = copy.deepcopy(data)
    if disabled:
        disabled = disabled.copy()

    ## Copy the input so as to leave it unmodified.
    # Discard self-dependencies and copy two levels deep.
    _data = {item: set(e for e in dep if e != item) for item, dep in data.items()}

    # Find all items that don't depend on anything.
    extra_items_in_deps = _reduce(set.union, _data.values()) - set(_data.keys())
    # Add empty dependences where needed.
    _data.update({item:set() for item in extra_items_in_deps})
    while True:
        ordered = set(item for item, dep in _data.items() if len(dep) == 0)
        if not ordered:
            break
        if disabled:
            if (ordered - disabled):
                yield ordered - disabled 
            disabled.update(set(item for item, dep in _data.items() if dep & disabled))
        else:
            yield ordered
        _data = {item: (dep - ordered)
                for item, dep in _data.items()
                    if item not in ordered}
    if len(_data) != 0:
        raise CircularDependencyError(_data)


def toposort_flatten(data, sort=True, disabled = set()):
    """\
Returns a single list of dependencies. For any set returned by
toposort(), those items are sorted and appended to the result (just to
make the results deterministic).
## Args
- **data** - the dependency graph
  dependencies are expressed as a dictionary whose keys are items
  and whose values are a set of dependent items. 
- **sort**(True) - should each batch be sorted
       
- **disabled**(optional) - Set of items which, with their dependents, should not be
  included in the output
"""

    result = []
    for d in toposort(data,disabled):
        result.extend((sorted if sort else list)(d))
    return result
