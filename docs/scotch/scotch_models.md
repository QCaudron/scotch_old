Title: scotch Model Definitions



# scotch models

_scotch_ models are JSON files that describe stochastic systems by their state space, their 
parameters, and a list of *reactions* between states. As with all [continuous-time Markov 
processes](http://en.wikipedia.org/wiki/Continuous-time_Markov_chain), state spaces must be 
finite or countable

```
{
    "States" : [
        "S",
        "I",
        "R"
    ],

    "InitialConditions" : {
        "I" : 1,
        "R" : 0,
        "S" : 99
    },

    "Parameters" : {
        "gamma" : "1/14",
        "r0" : "18"
    },

    "Reactions" : [
        [
            "S",
            "I",
            "r0 * gamma * S * I / (S+I+R)"
        ],
        [
            "I",
            "R",
            "gamma * I"
        ]
    ]
}
```
