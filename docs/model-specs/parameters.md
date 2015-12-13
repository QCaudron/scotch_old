# Parameters

Like `InitialConditions`, the `Parameters` field of _scotch_ model JSON files is a dictionary. Each key is the name of a parameter, as a string. Each value is a string expression for the value of that 
parameter.

```python
"Parameters" : {
    "alpha" : "1/10",
    "beta" : "1 + sin(2 * pi * time)"
}
```

Values are required to be strings because parameter values are parsed into expressions that can be evaluated as lambdas. This allows a number of functions to be used :

- `sin`, `sinh`, `arcsin`, `arcsinh`
- `cos`, `cosh`, `arccos`, `arccosh`
- `tan`, `tanh`, `arctan`, `arctanh`
- `exp`, `expm1` ( exp(x) - 1 )
- `log`, `log10`, `log2`, `log1p` ( log(1+x) ) 
- `ceil`, `floor`, `abs`
- `sinc`
- `square`, `sqrt`
- `sign` ( returns +1 or -1 )
- `time`

A number of reserved keywords also allow access to constants and to the explicit value of time :

- `pi`
- `time` ( allows time-dependent parameter rates to be used )

As an example, `sin(2 * pi * sqrt(F) * time)` is a legal part of a parameter value, if you have declared F as a state variable; this particular example allows parameters to vary sinusoidally in time. 
The `time` keyword is replaced by the numerical value of time during simulation. Parameters can therefore be state-dependent and time-dependent; they cannot, however, be written in terms of other parameters.

All numerical values are cast as floats, so expressions like `1/10` will be evaluated as 0.1.

Allowed operators are :

- `+`
- `-`
- `*`
- `/`
- `**`
- `(`, `)`

Currently, custom functions that cannot be written with this syntax will not evaluate. 
