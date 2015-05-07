# Documentation

## Model API


### Creating a model object

Creating a blank model is as simple as :
```python
model = scotch.model()
```

A natural place to go from here is then to call the wizard to help you generate the full model for simple systems, or perhaps just a backbone if it's a more complicated model :
```python
model.wizard()
```
More on the wizard below.


Alternatively, you can pass the filename of a JSON file containing a **scotch** model :
```python
model = scotch.model("mymodel.json")
```

### Using the wizard
Calling `model.wizard()` will invoke the wizard to walk you through model creation. You'll be asked for a number of things :

- A list of state variables, and their initial conditions
- A list of parameters, and their values
- A list of events, characterised by their rates and their effects on the state variables

State variables are to be entered as a comma-separated list. Let's say you're simulating a simple birth-death process, specifying males and females. You might then enter two states : 
```
F, M
```

Initial conditions are required to be integers. You will be asked for the initial value for each state, one at a time. Hit Enter between initial conditions. Perhaps we start like this : 
```
F : 2000
M : 1000
```

Parameters for this model might include a reproduction rate, and perhaps two death rates, one for females and one for males. The wizard asks for a comma-separated list of parameter names. You might enter :
```
birth, death_f, death_m
```

The wizard then asks for their values. Currently, parameters are fixed in value, but you have access to a few functions to make things interesting. Let's say we want our time to be in units of years, and we want the reproduction rate to be seasonal with annual periodicity. We might go for something like :
```
birth : 20/1000 * (M+F) * (1 + sin(2 * pi * time))
```


### Saving models
Models can be saved to file using
```python
model.save("mymodel.json")
```


