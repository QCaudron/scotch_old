# Initial Conditions

The `InitialConditions` field of _scotch_ model JSON files is a dictionary. Every entry in the `States` field must be a key in the `InitialConditions` dictionary, as a string. The value of each entry 
needs to be an integer initial value for that state variable.

```python
"InitialConditions" : {
    "Var1" : 100,
    "Var2" : 42,
    "Var3" : 0
}
``` 
