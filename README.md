# A tolerant toposort

Extends toposort to support disabled nodes, returning batches of node independent of disabled nodes


The use case was:
- To process all nodes: iterating through the batches supplied by toposort
- Whilst processing, nodes might be found to be disabled
- Nodes could not be processed if dependee(?) nodes were disabled
- Fixing, aka re-enabling nodes, took time
- Processing took time
- Once a node was processed, it needed no further processing

(think building packages... )

Requirements
- have the best handle on the number of disabled nodes (process as much as possible)
- Concurrently be able to:
  -   Process nodes
  -   Fix nodes


Using default toposort, as a node was found disabled, it required enabling (fixing) before any more nodes could be iterated
, and potentially more disabled nodes discovered

With tolerant toposort:
- Processing of all independant ( of disabled ) nodes can be attempted
- As disabled nodes are encountered they can be added to the set, and a revised batch set created
- Processing can then continue until all possible nodes have been attempted
- The maximum set of disabled nodes is returned
- 
# Usage
```python
def process()
    """
    perform a once-only process on a node.
    return the success of the proceess
    """
    return true;
def main()
    disabled=set()
    already_processed=set() # persist this between runs!!
    while(true):
        batches = toposort(get_graph(),disabled)
        break if ! batches
        processedAny= false
        try:
        for batch in batches:
            for node in batch:
            next if already_processed(node)
            if process(node):
                already_processed.add(node)
                processedAny= true
            else:
                raise ProcessException(node)
        break if !processedAny
        except ProcessException as be:
        disabled.add(be.node)
main()
```

# API

Allows a set disabled nodes to be passed to toposort

The disabled nodes, and any of their dependents, will not be returned in a batch

<img src="./doc/tiny.png" width="400">

<img src="./doc/small.png" width="400">

# Testing
```bash
 nosetests
 python3 setup.py test
 ```
