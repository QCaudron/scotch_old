<img src="https://raw.githubusercontent.com/QCaudron/scotch/master/docs/images/logo.jpg" style="width: 200px;" />

_scotch_ implements algorithms for **s**tochastic, **co**ntinuous-**t**ime **ch**ains, or 
Markov processes. We are currently in alpha release; contributions are very welcome. For pull requests or bug reports, find us on [Github](http://qcaudron.github.io/scotch). 

Stochastic systems are described by their state space and the transitions between them. _scotch_ can simulate stochastic systems with discrete state space


random walks, systems can be described by differential equations, 
and finite state machines, or any ( we think ) stochastic systems with finite state spaces.

We're in the process of rewriting some of the model definition language to generalise to a larger range of models. Both the package and documentation are in semi-active development - watch this space.



## Structure of these docs 

This will get removed, just a note for me :

- Scotch docs : documentation on the package; model definition, using the package
- Markov Processes : just a few pages about CTMC, what they can do, what models can be described as Markov chains. Also simulation algorithms, steady-state results, ...
- Examples : a few example scotch models to be used as a tutorial
- Model repository : maybe a few finished model JSON files to download ?


## Roadmap

#### Currently implemented :

- interactive "wizard" for full model specification
- Gillespie's algorithm
- tau-leaping algorithm
- a quick-plot method


#### For the future :

- adaptive timestepping in tau-leaping
- generating trace distributions with credible intervals
- parameter inference

