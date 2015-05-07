# Quick Start


<link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/KaTeX/0.2.0/katex.min.css">
<script src="//cdnjs.cloudflare.com/ajax/libs/KaTeX/0.2.0/katex.min.js"></script>


[TOC]


In this quick-start, we'll implement the basic [Susceptible-Infected-Recovered](http://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology) epidemiological model. This compartmental model is typically described by a system of deterministic, ordinary differential equations :

<div id="SIR_S" class="katex"></div><br /><p />
<div id="SIR_I" class="katex"></div><br /><p />
<div id="SIR_R" class="katex"></div><br /><p />

In the case of small populations, the continuous property of the state space can be a poor assumption, and we may prefer to simulate each individual in the population as separate entities. We'll phrase this model in the language of discrete-state stochastic processes, particularly that of continuous-time Markov chains. 


### Using the Wizard

_scotch_ models are defined in JSON format. For the SIR model above, it would look like this :

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




### Importing the model

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






### Simulating the model

In order to get sample trajectories of your stochastic model, simply call `model.simulate(tmax)`. For example :
```python
t, trace = model.simulate(30)
```
will simulate the model and return the time values in `t`, and the state space in `trace`. You can then `plt.plot(t, trace)`. See the [documentation on scotch.simulate](documentation/simulate/) for different simulation algorithms and options.

If you're just looking to inspect your system visually, you can call `model.plot`. This takes exactly the same arguments as whichever simulation algorithm you're using.

```python
model.plot(30)
```

PHOTO GOES HERE





### Sampling trace expectations and credible intervals

Watch this space.






    <script>
    var SIR_S = "\\displaystyle \\frac{\\text{d}{S}}{dt} = -\\frac{\\beta \\, S \\, I}{N}";
    var SIR_I = "\\displaystyle \\frac{\\text{d}{I}}{dt} = \\frac{\\beta \\, S \\, I}{N} - \\gamma \\, I";
    var SIR_R = "\\displaystyle \\frac{\\text{d}{R}}{dt} = \\gamma \\, I";

    katex.render(SIR_S, document.getElementById('SIR_S'));
    katex.render(SIR_I, document.getElementById('SIR_I'));
    katex.render(SIR_R, document.getElementById('SIR_R'));
    </script>
