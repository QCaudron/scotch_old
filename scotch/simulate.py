# Simulation algorithms
import numpy as np
import helpers








# Gillespie algorithm
def gillespie(model, tmax, track=False, incremental=False) :

	# Initialise
	t = [0]
	model.build(silent=True) # initialise model
	trace = model.X[:]
	rates = np.zeros(model.N_reactions)

	"""
	# If we're tracking individuals, generate IDs for everyone
	if track :
		if incremental : 
			events = {}
		else :

		maxID = 0
		individuals = {}
		statespace = {}
		for i, state in enumerate(model.states) :
			statespace[state] = range(maxID, maxID + model.X[i])
			maxID += model.X[i]
		individuals[0] = statespace # add initial IDs to individuals for t=0
	"""

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
		trans = np.where(np.random.uniform() < np.cumsum(rates / np.sum(rates)))[0][0]
		model.X += model.transition[:, trans]


		# If we're tracking, keep track of the transition
		#if track :
		#	if incremental :

		
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










def tauLeap(model, tmax, tau=1, track=False, incremental=False) :

	# Initialise
	t = [0]
	trace = model.X[:]
	rates = np.zeros(model.N_reactions)

	# Start the progress bar
	helpers.progBarStart()


	"""
	# If we're tracking individuals, generate IDs for everyone
	if track :
		maxID = 0
		individuals = {}
		for i, state in enumerate(model.states) :
			individuals[state] = range(maxID, maxID + model.X[i])
			maxID += model.X[i]
	"""

	cappedReactions = [np.where(model.transition[:, i] == -1)[0] for i in range(model.N_reactions)] # reaction takes one away from here


	# Continue until we hit tmax
	while t[-1] < tmax :

		# Compute a rates vector 
		rates = [rate(model.X) for rate in model.rates]

		assert (np.array(rates) < 0).sum() == 0, "Negative rates, you die now. % s" % rates

		# Determine which events occurred after ensuring that there's 
		# a valid transition, and update the state space
		if np.sum(rates) <= 0 :
			print "Stopping early - no valid transitions !"
			break

		# Correct so things don't go negative :		
		maxReactions = np.array([model.X[i] if len(i) == 1 else np.inf for i in cappedReactions], dtype=int)[:, 0]

		# Determine the number of times each transition happens in tau time
		estReactions = np.array([np.random.poisson(rate * tau) for rate in rates], dtype=int)
		doneReactions = np.min((maxReactions, estReactions), axis=0).astype(int)

		if not (doneReactions != estReactions).all() :
			print "Some reactions could not take place due to small state variable."
			print "Perhaps tau is too large."

		# Increase time
		# if there's at least one reaction but we can't do them all
		if (doneReactions != estReactions).all() and np.sum(estReactions) > 0 :
			t.append(t[-1] + tau * float(np.sum(doneReactions)) / np.sum(estReactions))
		else :
			t.append(t[-1] + tau)



		print "State space", model.X
		print "Done reactions", doneReactions
		print "State Space Change", np.sum(model.transition * doneReactions, axis=1)
		print "Est", estReactions
		print "Max reactions", maxReactions
		# Update the state space
		model.X += np.sum(model.transition * doneReactions, axis=1).astype(int)



		assert (model.X < 0).sum() == 0, "Negative state space, you DIE NAO"


		# Append new state space to trace
		trace = np.vstack((trace, model.X))


		# Update progress bar
		helpers.progBarUpdate(t[-2:], tmax)


	# Reset state space
	model.X = np.array([model.initconds[x] for x in model.states], dtype=int)

	return (t, trace)





	# PROBLEM :
	# Max reactions should take into account total outwards stream, not just per reaction











def sample(model, tmax, algorithm=gillespie) :
	pass