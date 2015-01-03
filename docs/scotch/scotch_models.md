Title: scotch Model Definitions

# scotch models

_scotch_ models are JSON files that describe stochastic systems by their state space, their parameters, and a list of *reactions* between states. As with all [continuous-time Markov processes](http://en.wikipedia.org/wiki/Continuous-time_Markov_chain), state spaces must be finite or countable.

**More info here.**

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

    "Reactions" : [
        {
            "r0 * gamma * S * I / (S+I+R)" : {
                "S" : -1,
                "I" : 1
            }
        },
        {
            "gamma * I" : {
                "I" : -1,
                "R" : 1
            }
        }
    ]
}
```
