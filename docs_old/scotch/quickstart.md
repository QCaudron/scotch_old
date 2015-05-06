# Quick Start


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




### Simulating the model

Watch this space.

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
