Title: Random Walk

# The Whisky-Fuelled Random Walk



### Scenario

After a night of enjoying substantial amounts of single malt whisky, a Python programmer must stumble home from the bar. With impaired motor skills, she staggers home, with each step either :
 
- bringing her closer to her bed with probability `p`,
- a backwards stumble with probability `q`,
- hovering on the spot to regain her balance with probability `r`.


We only wish to measure her distance from home, and thus define the state space as the one-dimensional variable `X`. We start `X` with an initial condition of one hundred steps away from her home. With probability `p`, `X` decreases by one; with probability `q`, `X` increases by one; and with probability `r`, `X` remains unchanged.



### _scotch_ model specification

We can express this system as a _scotch_ model as follows :

```
{
    "States" : [
        "X"
    ],

    "InitialConditions" : {
        "X" : 0
    },

    "Parameters" : {
        "p" : "0.5",
        "q" : "0.3",
        "r" : "0.2"
    },

    "Events" : [
        [
            "p", { "X" : 1 }
        ],
        [
            "q", { "X" : -1 }
        ]
    ]
}
```

Let's go through the model file, line by line. First, note that it's a [JSON](http://en.wikipedia.org/wiki/JSON) file, an open standard for data interchange that's easy for humans to read and for computers to parse. We'll use Python jargon to describe the data structures that make up the _scotch_ model file.

First, note that the whole thing is one big dictionary. There are a few required keys :

- `States`, a list of state variables;
- `InitialConditions`, a dictionary mapping state variables to their initial conditions;
- `Parameters`, a dictionary of parameter names and their values (as strings);
- `Events`, a dictionary mapping rates to events, which we'll see more closely soon.

The `States` entry might look like `"States" : ["X", "Y"]` if you wanted to simulate a random walk in two dimensions. It's just a list of state variables, as strings. Each element of the `States` list has to be a key in the `InitialConditions` dictionary, with the value being the integer initial condition for that state variable.

The `Parameters` entry is also a dictionary : each entry is a key-value pair mapping the parameter's name to its value. You don't need to declare a list of parameters on their own; we write them straight away with their values in the `Parameters` field. Note that the value must be given as a string.

`Events` is a dictionary. Each key is an expression defining the rate at which the event takes place. Each value is a dictionary of transitions that occur when that reaction takes place. In this example, at a rate `p`, the variable `D` decreases by one; with probability `q`, variable `D` increases by one; we've left out the `r`-rated reaction, as nothing happens here. If you wanted to include it, it would look like `"r" : [["D", 0]]"`, although this will slow down your simulations. The reason for the dictionary of dictionaries is because we could, in more complex models, have more than one transition per reaction. Say the random walk were in 2D. Then, with a certain probability, perhaps our drunk programmer would take a diagonal step; with our `X` and `Y` state variables, this reaction might look like,

```
{
    "s" : { "X" : 1, 
            "Y" : 1 }
}
```

That is, with probability `s`, we take a step that increases the X and Y coordinates by one each. This reaction is written as a dictionary, with an expression for the rate of the reaction as the key, and the value being a dictionary, with keys representing state variables and values representing the change in that state when the reaction occurs.

Finally, note that, in the language of random walks, we've described our parameters `p, q, r` as probabilities here. However, _scotch_ expects rates, and thus, the parameters need not sum to one.




### Simulation

Stuff here.