# Simulation algorithms
import numpy as np
import helpers


# Gillespie algorithm
def gillespie(model, tmax) :

	# Initialise
	t = [0]
	trace = model.X[:]
	rates = np.zeros(model.N_reactions)

	# Generate this many random uniforms at once, for speed
	randsize = 1000
	tlast = 0

	# Pregenerate some random numbers
	rand = np.random.uniform(size=1000)
	rcount = 0

	# Start the progress bar
	helpers.progBarStart()

	# Continue until we hit tmax
	while t[-1] < tmax :

		# Compute a rates vector
		rates = [rate(model.X) for rate in model.rates]


		# Determine which event occurred after ensuring that there's 
		# a valid transition, and update the state space
		if np.sum(rates) <= 0 :
			print "Stopping early - no valid transitions !"
			break


		# Draw a waiting time
		t.append(t[-1] + np.random.exponential(1./np.sum(rates)))


		# Update the state space
		model.X += model.transition[:, np.where(np.random.uniform() < np.cumsum(rates / np.sum(rates)))[0][0]]

		
		# At the end of randsize iterations, update randsize "adaptively"
		rcount += 1
		if rcount == randsize :
			rcount = 0
			randsize = max(1000, randsize * tmax / (tlast - t[-1]) - 1)
			rand = np.random.uniform(size=randsize)
			tlast = t[-1]

		
		# Append new state space to trace
		trace = np.vstack((trace, model.X))


		# Update progress bar
		helpers.progBarUpdate(t[-2:], tmax)


	# Reset state space
	model.X = np.array([model.initconds[x] for x in model.states], dtype=int)

	return (t, trace)










def tauLeap(model, tmax, tau=1) :

	# Initialise
	t = [0]
	trace = model.X[:]
	rates = np.zeros(model.N_reactions)

	# Start the progress bar
	helpers.progBarStart()


	# Continue until we hit tmax
	while t[-1] < tmax :

		# Compute a rates vector 
		rates = [rate(model.X) for rate in model.rates]

		# Determine which events occurred after ensuring that there's 
		# a valid transition, and update the state space
		if np.sum(rates) <= 0 :
			print "Stopping early - no valid transitions !"
			break


		# Determine the number of times each transition happens in tau time
		estReactions = [np.random.poisson(rate * tau) for rate in rates]

		# Correct so things don't go negative
		cappedReactions = [np.where(model.transition[:, i] == -1)[0] for i in range(model.N_reactions)] # reaction takes one away from here
		maxReactions = [model.X[i] if len(i) == 1 else np.inf for i in cappedReactions]
		doneReactions = np.min((maxReactions, estReactions), axis=0).astype(int)

		if (doneReactions != estReactions).all() :
			print "Some reactions could not take place due to small state variable."
			print "Perhaps tau is too large."

		# Increase time
		t.append(t[-1] + tau * float(np.sum(doneReactions)) / np.sum(estReactions))


		# Update the state space
		model.X += np.sum(model.transition * doneReactions, axis=1)


		# Append new state space to trace
		trace = np.vstack((trace, model.X))


		# Update progress bar
		helpers.progBarUpdate(t[-2:], tmax)


	# Reset state space
	model.X = np.array([model.initconds[x] for x in model.states], dtype=int)

	return (t, trace)














def sample(model, tmax, algorithm=gillespie) :
	pass