# Algorithms

[TOC]




## The Gillespie Algorithm
[Gillespie's algorithm](http://en.wikipedia.org/wiki/Gillespie_algorithm), also known as the Stochastic Simulation Algorithm, was first described in 1976. It's a popular and, more importantly, exact, dynamic Monte Carlo method, used in the simulation of stochastic systems. 

- DT Gillespie. [A general method for numerically simulating the stochastic time evolution of coupled chemical reactions](http://www.sciencedirect.com/science/article/pii/0021999176900413). _Journal of Computational Physics_ **22**, 403-434 (1976).
- DT Gillespie. [Exact stochastic simulation of coupled chemical reactions](http://pubs.acs.org/doi/abs/10.1021/j100540a008). _Journal of Physical Chemistry_ **81**, 2340–2361 (1977)





## Tau-Leaping
The [tau-leaping](http://en.wikipedia.org/wiki/Tau-leaping) algorithm is an approximation of Gillespie's algorithm that provides a trade-off between speed and accuracy. Instead of performing one event at a time, the tau-leaping algorithm estimates all of the events that occurred in a given interval of time [t, t+tau), based on the event rates at time t. It can run a great deal faster, but too large a step size can cause significant errors. 

-  Gillespie, DT. [Approximate accelerated stochastic simulation of chemically reacting systems](http://scitation.aip.org/content/aip/journal/jcp/115/4/10.1063/1.1378322). _Journal of Chemical Physics_ **115**, 1716–1711 (2001).






## Adaptive Tau-Leaping

Not yet implemented.

- Y Cao, DT Gillespie, and LR Petzold. [The adaptive explicit-implicit tau-leaping method with automatic tau selection](http://scitation.aip.org/content/aip/journal/jcp/126/22/10.1063/1.2745299). _Journal of Chemical Physics_ **126**, 224101 (2007).





## The Next-Reaction Method

Not yet implemented.

- MA Gibson and J Bruck. [Efficient exact stochastic simulation of chemical systems with many species and many channels](http://pubs.acs.org/doi/abs/10.1021/jp993732q). _Journal of Physical Chemistry A_ **104**, 1876–1889 (2000).