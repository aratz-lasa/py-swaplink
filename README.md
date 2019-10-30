# py-swaplink
[![Build Status](https://travis-ci.com/aratz-lasa/py-swaplink.svg?branch=master)](https://travis-ci.com/aratz-lasa/py-swaplink)
[![codecov](https://codecov.io/gh/aratz-lasa/py-swaplink/branch/master/graph/badge.svg)](https://codecov.io/gh/aratz-lasa/py-swaplink)

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

swaplink implemented in Python.

## What is Swaplink
Swaplinks builds a random peer-to-peer unstructured overlay, in which each node’s degree is proportional to its desired degree capacity. Then, uses random walks over the generated random graph to do random node sampling.

It gives quite-precise control over both the probability that a node is selected and the overhead of visited nodes when executing peer sampling.

It is efficient, scalable, robust and simple, while limiting tuning-knobs to just the 'desired-load'.

## Usage
```python
from swaplink import Swaplink

def callback(neighbors):
    ...

async def main():
    host = "127.0.0.1"
    port = 5678
    num_links = 5  # relative load on your node
    boostrap_nodes = [("127.0.0.1", 7777)]

    network = Swaplink(host, port)
    await network.join(num_links, boostrap_nodes)
    random_node = await network.select()
    neighbors = network.list_neighbours(callback)
    ...
    await network.leave()
```

## References
* [Swaplink paper](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.365.9926) - Vivek Vishnumurthy and Paul Francis. On heterogeneous over-lay construction and random node selection in unstructured p2pnetworks. InProc. IEEE Infocom, 2006.
* [Swaplink evaluation paper](https://www.usenix.org/event/usenix07/tech/full_papers/vishnumurthy/vishnumurthy.pdf) - V. Vishnumurthy and P. Francis.  A Comparison of Structured andUnstructured P2P Approaches to Heterogeneous Random Peer Selection.InProceedings of the USENIX Annual Technical Conference, pages 1–14, 2007.
