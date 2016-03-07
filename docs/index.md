<img src="https://raw.githubusercontent.com/QCaudron/scotch/master/docs/images/logo.jpg" style="width: 200px;" />

_scotch_ implements algorithms for **s**tochastic, **co**ntinuous-**t**ime **ch**ains, or Markov processes. We are currently in alpha release; contributions are very welcome. For pull requests or bug reports, find us on [Github](https://github.com/QCaudron/scotch). The core developers are [Quentin Caudron](http://quentincaudron.com) and [Ruthie Birger](http://ruthiebirger.com).





## Contents

- **Quick-Start** : dive straight into describing stochastic processes and simulating them with _scotch_.
- **Model Specifications** : the full specs for _scotch_ model files.
- **Scotch API and Docs** : docs for model building, simulating, sampling, and plotting _scotch_ systems.
- **Examples** : a series of example _scotch_ models that work out of the box.





## Roadmap

#### Currently implemented :

- interactive, text-based "wizard" for full model specification
- Gillespie's (SSA) algorithm
- tau-leaping algorithm
- a quick-plot method for single realisations
- repeat trajectory sampling and bootstrapping confidence intervals
- complete event tracking


#### For the future :

- Gibson-Bruck algorithm
- adaptive timestepping in tau-leaping
- parameter inference



## Bug Reports and Contributing

Please let us know about bugs as issues on [Github](http://github.com/QCaudron/scotch). Pull requests are also absolutely welcome !



## Dependencies

#### Required 

- Python >= 2.7
- Numpy
- Scipy (for `model.sample()` and `model.plotsamples()`)
- Matplotlib (for `model.plot()` and `model.plotsamples()`)

#### Optional

- Seaborn




<a href="https://github.com/QCaudron/scotch"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://camo.githubusercontent.com/38ef81f8aca64bb9a64448d0d70f1308ef5341ab/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f6461726b626c75655f3132313632312e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png"></a>
