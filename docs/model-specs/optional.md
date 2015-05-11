# Optional Entries

These entries are not required to fully define a _scotch_ model. However, they may be inserted into the JSON file at various points.

### Filename

The `Filename` field takes the full path for the location of the model's JSON file as a string :
```python
"Filename" : "/Users/qcaudron/scotch/models/myfile.json"
```

 When you save the model by calling `model.save("/some/directory/model.json")`, the `Filename` entry is automatically added to the JSON file. Next time, you can then call `model.save()` without 
specifying a path, and the model will be saved with its default filename - the one you specifed last time. 

If you call `model.save()` without a filename, and `Filename` is not defined in the model's optional entries, the file will be saved in the current working directory under the filename `scotch_model.json`.



### Default algorithm

The `default_algorithm` field also takes a string.
```python
"default_algorithm" : "gillespie"
```

Every time you call any function that invokes _scotch_'s simulator without specifying the algorithm you want to use, then the `default_algorithm` is used. This entry is added to the model as soon as 
the model is built - that is, as soon as the wizard finishes, or as the first step in any simulation ( as long as you aren't propagating your state space from the last simulation ). If you don't 
specify a default algorithm, the default algorithm is set to `gillespie`. Valid entries are :

- `gillespie`
- `tauLeap`

