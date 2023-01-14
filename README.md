---

# Table of Contents
* [Tolerant toposort](#Tolerant-toposort)
* [Examples](#Examples)
	* [Simple](#Simple)
	* [Less Simple](#Less-Simple)
* [Use Case](#Use-Case)
* [Typical Usage (ymmv)](#Typical-Usage-(ymmv))
* [API](#API)
	* [Module `tolerant.toposort`](#Module-`tolerant.toposort`)
		* [Functions](#Functions)
		* [Classes](#Classes)
* [Testing](#Testing)
* [Install](#Install)

# Tolerant toposort

Extends the Python package [toposort](https://pypi.org/project/toposort) to support disabled nodes within the graph   
**Tolerant toposort** returns batches of nodes which are independent of disabled nodes

```python
data = {
            2:  {11},
            9:  {11, 8},
            10: {11, 3},
            11: {7, 5},
            8:  {7, 3},
        }
disabled = {5}
toposort(data, disabled)
[{3, 7}, {8}]
```


# Examples
## Simple
Item  1 depends on Item 2, depends on 3, depends on 4   
With Item 3 disabled both 2 and 1 are implicitly disabled.   
However, using tolerant toposort, we find we can still process Item 4

<img src="./doc/tiny.png" width="400">

```python
data = {
            1:  {2},
            2:  {3},
            3:  {4},
        }
disabled = {3}
result = toposort(data, disabled)
[{4}]
```

## Less Simple
A more complicated graph with Item 7 disabled   
Again, using tolerant toposort, we find we can still process Items 3, 5, then 10, and then 12:

<img src="./doc/small.png" width="400">

```python
data = {2: {2,11},
        9: {11, 8, 10},
       10: {3},
       11: {7, 5},
        8: {7, 3},
       12: {10},
       }
disabled = {7}
result = toposort(data, disabled)
[{3, 5}, {10}, {12}]
```

# Use Case

The original use case was building packages.

The aim was to process(build) as many nodes(packages) as possible in a tree of nodes:
- Whilst processing, a node might fail to be processed
- Or the node might be known to be failed prior to processing
- If a node was failed then it and its dependants could not be processed
- Fixing, aka re-enabling nodes, took time
- Processing nodes took time
- Processing a node only to find its dependant was failed, took time
- Once a node was processed, it needed no further processing


The main issue was if a node failed ( or was failed prior), then no more nodes could safely be processed, and that switched what should have been concurrent:
- fixing nodes
- processing nodes

into a repetition of process batches,node fails,fix node,process batches,node fails,fix node,process batches...


Requirements for the improvements:
- To have the best handle on the number of disabled nodes (ie attempt to process as many nodes much as possible)
- Concurrently be able to:
  -   repeatedly process batches, revealing failed nodes as they appear, recalculate batches, continue processing
  -   Fix failed nodes as they 'appear', removing them from the disabled list as they are supposedly fixed


With tolerant toposort:
- Processing of all independant ( of disabled ) nodes can be attempted
- As disabled nodes are encountered they can be added to the disabled set, and a revised batch set created
- Processing can then continue until all possible nodes have been attempted
- The maximum set of disabled nodes is returned

# Typical Usage (ymmv)
```python
from tolerant.toposort import toposort,CircularDependencyError
def get_graph():
	""" build and return your graph """
    return [1:{2}]
def process():
    """
    perform a once-only process on a node.
    return the success of the proceess
    """
    return true;
def main():
    disabled=set()          # add any known failed items at start-up
    already_processed=set() # persist this between runs!!
    graph = get_graph()
    while(true):
        batches = toposort(graph,disabled)
        # our work is done ( bar fixing any disabled)
        break if ! batches
        processedAny = false
        try:
            for batch in batches:
                for node in batch:
                    next if already_processed(node)
                    if process(node):
                        already_processed.add(node)
                        processedAny= true
                    else:
                        raise ProcessException(node)
        # our work is done ( bar fixing any disabled)
        break if !processedAny
        except ProcessException as pe:
            # pe.node can now be concurrently 'fixed'
            disabled.add(pe.node)
    if ! disabled:
        # we are done
    	pass
main()
```

# API
---
  
## Module `tolerant.toposort`

generates batches of dependant items which are enabled and do not depend
    on disabled items

Based on [toposrt()]<https://pypi.org/project/toposort>)
with these changes:
-   toposort and toposort_flatten take an optional set of disabled items.
    These disabled items, and their dependents, will not be included
    in the returned batch(es) 

### Functions


#### Function `toposort`



```python
def toposort(
    data,
    disabled=set()
  )
```

Dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items.  
Returns a list of sets in topological order. The first set consists of items with no
dependences, each subsequent set consists of items that depend upon
items in the preceeding sets.


###### Args
- **data** - the dependency graph
dependencies are expressed as a dictionary whose keys are items
and whose values are a set of dependent items. 

- **disabled**(optional) - Set of items which, with their dependents, should not be
  included in the output

###### Returns
- a list of sets in topological order which are not disabled, or depend on
a disabled item.  
The first set consists of items with no dependences, each subsequent set 
consists of items that depend upon items in the preceeding sets.

#### Function `toposort_flatten`



```python
def toposort_flatten(
    data,
    sort=True,
    disabled=set()
  )
```

Returns a single list of dependencies. For any set returned by
toposort(), those items are sorted and appended to the result (just to
make the results deterministic).
###### Args
- **data** - the dependency graph
  dependencies are expressed as a dictionary whose keys are items
  and whose values are a set of dependent items. 
- **sort**(True) - should each batch be sorted
       
- **disabled**(optional) - Set of items which, with their dependents, should not be
  included in the output

### Classes


#### Class `CircularDependencyError`



```python
class CircularDependencyError(
    data
)
```

An item _eventually_ depends on itself

**NOTE** : we tolerate items _directly_ depending on themeselves

#### Args
- **data** : the list containing  the circular dependency

# Testing
```bash
 nose2
 python3 setup.py test
```
# Install
```bash
 sudo python3 setup.py install
```