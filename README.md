# py-swaplink
[![Build Status](https://travis-ci.com/aratz-lasa/py-swaplink.svg?branch=master)](https://travis-ci.com/aratz-lasa/py-swaplink)
[![codecov](https://codecov.io/gh/aratz-lasa/py-swaplink/branch/master/graph/badge.svg)](https://codecov.io/gh/aratz-lasa/py-swaplink)

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

swaplink implemented in Python.

## What is Swaplink
Swaplinks builds a random peer-to-peer unstructured overlay, in which each node’s degree is proportional to its desired degree capacity. And then uses random walks over that graph to do node selection. 

It gives quite-precise control over both the probability that a node is selected and the overhead of visited nodes while random walks.

It is efficient, scalable, robust and simple, while limiting tuning-knobs to just 'desired-load' or 'capacity'.

## Usage

## References
* [Swaplink paper](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.365.9926) - Vivek Vishnumurthy and Paul Francis. On heterogeneous over-lay construction and random node selection in unstructured p2pnetworks. InProc. IEEE Infocom, 2006.
* [Swaplink evaluation paper](https://www.usenix.org/event/usenix07/tech/full_papers/vishnumurthy/vishnumurthy.pdf) - V. Vishnumurthy and P. Francis.  A Comparison of Structured andUnstructured P2P Approaches to Heterogeneous Random Peer Selection.InProceedings of the USENIX Annual Technical Conference, pages 1–14, 2007. 




