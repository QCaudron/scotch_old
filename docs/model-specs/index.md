# Model Specification

**scotch** models are [JSON](http://en.wikipedia.org/wiki/JSON) files with a handful of required entries, and a number of optional ones. The minimal **scotch** model file contains :

- `Events`
- `States`
- `Initial Conditions`
- `Parameters`

This is sufficient to describe a stochastic model. Optional entries are :

- `default_algorithm`
- `Filename`