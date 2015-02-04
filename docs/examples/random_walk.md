Title: Random Walk

# The Whisky-Fuelled Random Walk



### Scenario

After a night of enjoying substantial amounts of single malt scotch, a Python programmer must stumble home from the bar. With impaired motor skills, she staggers home, with each step either :
 
- bringing her closer to her bed with probability `p`,
- a backwards stumble with probability `q`,
- hovering on the spot to regain her balance with probability `r`.


We only wish to measure her distance from home, and thus define the state space as the one-dimensional variable `D`. We start `D` with an initial condition of one hundred steps. With probability `p`, `D` decreases by one; with probability `q`, `D` increases by one; and with probability `r`, `D` remains unchanged.



### _scotch_ model specification

We can express this system as a _scotch_ model as follows :

```
{
    "States" : [
        "D"
    ],

    "InitialConditions" : {
        "D" : 100,
    },

    "Parameters" : {
        "p" : "0.5",
        "q" : "0.2",
        "r" : "0.3"
    },

    "Reactions" : [
        {
            "p" : { "D" : -1 }
        },
        {
            "q" : { "D" : 1 }
        }
    ]
}
```

Let's go through the file line by line. We'll use Python jargon to describe the data structures that make up the _scotch_ model file.

First, note that the whole thing is one big dictionary. There are a few required keys :

- `States`, a list of state variables;
- `InitialConditions`, a dictionary mapping state variables to their initial conditions;
- `Parameters`, a dictionary of parameter names and their values (as strings);
- `Reactions`, a dictionary mapping rates to transitions, which we'll see more closely soon.

The `States` entry might look like `"States" : ["X", "Y"]` if you wanted to simulate a random walk in two dimensions. It's just a list of state space names, as strings. There has to be one entry in the `InitialConditions` dictionary per entry in the `States` list.

The `Parameters` entry combines this style : each entry is a key-value pair mapping the parameter's name to its value. Note that the value must be given as a string - this is because the value can contain numerical expressions (for more on this, see the _scotch_ model page, to be created and linked soon...).

`Reactions` is a dictionary. Each key is an expression defining the rate of the reaction. Each value is a dictionary of transitions that occur when that reaction takes place. In this example, at a rate `p`, the variable `D` decreases by one; with probability `q`, variable `D` increases by one; we've left out the `r`-rated reaction, as nothing happens here. If you wanted to include it, it would look like `"r" : [["D", 0]]"`, although this will slow down your simulations. The reason for the dictionary of dictionaries is because we could, in more complex models, have more than one transition per reaction. Say the random walk were in 2D. Then, with a certain probability, perhaps our drunk programmer would take a diagonal step; with our `X` and `Y` state variables, this reaction might look like,

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