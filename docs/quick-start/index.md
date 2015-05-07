# Quick Start


<link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/KaTeX/0.2.0/katex.min.css">
<script src="//cdnjs.cloudflare.com/ajax/libs/KaTeX/0.2.0/katex.min.js"></script>


[TOC]


In this quick-start, we'll implement the basic [Susceptible-Infected-Recovered](http://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology) epidemiological model. This compartmental model is typically described by a system of deterministic, ordinary differential equations :

<div id="SIR_S" class="katex"></div><br /><p />
<div id="SIR_I" class="katex"></div><br /><p />
<div id="SIR_R" class="katex"></div><br /><p />

In the case of small populations, the continuous property of the state space can be a poor assumption, and we may prefer to simulate each individual in the population as separate entities. We'll phrase this model in the language of discrete-state stochastic processes, particularly that of continuous-time Markov chains. 


### The model file

_scotch_ models are defined in JSON format. For the SIR model above, with time in days, it would look like this :

```
{
    "States" : [
        "S",
        "I",
        "R"
    ],

    "InitialConditions" : {
        "S" : 99,
        "I" : 1,
        "R" : 0
    },

    "Parameters" : {
        "r0" : "18",
        "gamma" : "1/14"
    },

    "Events" : [
        [
            "r0 * gamma * S * I / (S+I+R)",
            {
                "S" : -1,
                "I" : 1
            }
        ],
        [
            "gamma * I",
            {
                "I" : -1,
                "R" : 1
            }
        ]
    ]
}
```

You can download this file [here](files/sir.json).




### Running the model

Let's boot up _scotch_ and begin simulating the system.

```python
import scotch

# Read in the scotch model file
model = scotch.model("sir.json")
```

This will return :
```text
scotch model with 3 states, 2 parameters, and 2 events.

States :
S, initial condition = 99
I, initial condition = 1
R, initial condition = 0

Parameters :
r0 = 18
gamma = 1/14
```

Let's see what happens over the course of thirty days.

```python
model.plot(30)
```
![Stochastic realisation of the SIR model.](/images/sir.png)

This is one realisation of the system. Perhaps we instead want to see average dynamics. Let's get the mean of one hundred trajectories and bootstrap some confidence intervals. We'll use the tau-leaping algorithm for speed.

```python
model.plotsamples(30, algorithm="tauLeap", tau=0.25, trajectories=100, bootstrap=500)
```
![Mean dynamics of the stochastic SIR model.](/images/sir_mean.png)


Both `.plot` and `.plotsamples` call `.simulate` under the hood. If you want _scotch_ to return the traces of simulations to you, simply call
```python
t, trace = model.simulate(30)
```

See the documentation for the complete API reference.




<script>
var SIR_S = "\\displaystyle \\frac{\\text{d}{S}}{dt} = -\\frac{\\beta \\, S \\, I}{N}";
var SIR_I = "\\displaystyle \\frac{\\text{d}{I}}{dt} = \\frac{\\beta \\, S \\, I}{N} - \\gamma \\, I";
var SIR_R = "\\displaystyle \\frac{\\text{d}{R}}{dt} = \\gamma \\, I";

katex.render(SIR_S, document.getElementById('SIR_S'));
katex.render(SIR_I, document.getElementById('SIR_I'));
katex.render(SIR_R, document.getElementById('SIR_R'));
</script>
