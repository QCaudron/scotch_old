scotch
======

*Stochastic COntinuous Time CHains*

`scotch` is a package for simulating, sampling from, and interfering the paraters of continuous-time Markov processes. It's currently in pre-alpha.



Installation
------------

Download the contents of the repository, then call `python setup.py install` from command-line.


Usage
-----

```
import scotch

model = scotch.model()
```



TO DO 
-----

- Runtime warnings ( in tau-leaping, when we draw more transitions than are possible, for 
example )
- Sampling ( generate N realisations, compute summary statistics )
- Inference ( MLE methods for parameters )
- Simulation ( implicit tau-leaping ? Adaptive timestepping )
- Forecasting ( filtering methods ? )
- Parallelisation ( primarily, shared-memory )
