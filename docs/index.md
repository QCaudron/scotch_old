<img src="https://raw.githubusercontent.com/QCaudron/scotch/master/docs/images/logo.jpg" style="width: 200px;" />

_scotch_ implements algorithms for **s**tochastic, **co**ntinuous-**t**ime **ch**ains, or Markov processes. We are currently in pre-alpha release; contributions are very welcome. For pull requests or bug reports, find us on [Github](http://qcaudron.github.io/scotch). The core developers are [Quentin Caudron](http://quentincaudron.com) and [Ruthie Birger](http://ruthiebirger.com).

We're in the process of rewriting some of the model definition language to generalise to a larger range of models. Both the package and documentation are in semi-active development - watch this space.



## Contents

- **scotch** : quick-start, package API, model specification
- **Markov chains** : a short primer on Markov chains and descriptions on algorithms for simulating them
- **Examples** : a few example scotch models, to be used as a tutorial
- **Model repository** : maybe a few finished model JSON files to download ?




## Roadmap

#### Currently implemented :

- interactive "wizard" for full model specification
- Gillespie's algorithm
- tau-leaping algorithm
- a quick-plot method


#### For the future :

- adaptive timestepping in tau-leaping
- generating trace distributions with credible intervals
- parameter inference

