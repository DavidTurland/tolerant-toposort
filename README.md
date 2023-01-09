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
However, using tolerant toposort, we can still process Item 4
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
Again, using tolerant toposort, we can still process Items 3, 5, then 10 and then 12:
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
See [pdoc](https://pdoc.dev/)-generated [API](doc/tolerant/index.html)

# Testing
```bash
 nose2
 python3 setup.py test
```
# Install
```bash
 sudo python3 setup.py install
```
# Create Documention
```bash
pdoc --html --output-dir doc src/tolerant
```
