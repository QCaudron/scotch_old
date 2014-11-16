# Simulation algorithms
import numpy as np


# Gillespie algorithm
def gillespie(model, tmax) :

	t = [0]
	trace = model.X[:]
	rates = np.zeros(model.N_reactions)

	# Pregenerate some random numbers
	rand = np.random.uniform(size=1000)
	rcount = 0

	while t[-1] < tmax :

		# Compute a rate vector
		for i in range(model.N_reactions) :
			rates[i] = model.rates[i](model.X)

		# Draw a waiting time
		t.append(t[-1] + np.random.exponential(1./rates.sum()))

		# Determine which event occurred after ensuring that there's 
		# a valid transition, and update the state space
		if rates.sum() == 0 :
			break
		model.X += model.transition[:, np.where(rand[rcount] < np.cumsum(rates / rates.sum()))[0][0]]
		rcount = (rcount + 1) % 1000 # update random number counter

		trace = np.vstack((trace, model.X))


	# Reset state space
	model.X = np.array([model.initconds[x] for x in model.states], dtype=int)

	return (t, trace)









def sample(model, tmax, algorithm=gillespie) :
	pass