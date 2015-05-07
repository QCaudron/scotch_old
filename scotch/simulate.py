# Simulation algorithms
import numpy as np
import helpers




# Gillespie algorithm
def gillespie(model, tmax, track=False, silent=False, propagate=False, **kwargs) :

	# Initialise
	t = [0]

	if not propagate :
		model.build(silent=True) # initialise model

	trace = model.X[:]


	# Generate this many random uniforms at once, for speed
	randsize = 1000
	tlast = 0

	# Pre-allocate matrix of tracked reactions
	if track:
		tracked_trans_array = np.zeros((model.N_events,randsize))
		tcount = 0

	# Pregenerate some random numbers
	rand = np.random.uniform(size=1000)
	rcount = 0

	# Start the progress bar
	if not silent :
		helpers.progBarStart()



	# Continue until we hit tmax
	while t[-1] < tmax :

		# Compute a rates vector
		rates = [rate(model.X, t[-1]) for rate in model.rates]


		# Determine which event occurred after ensuring that there's 
		# a valid transition, and update the state space
		if np.sum(rates) <= 0 :
			if not silent :
				print "Stopping early - no valid transitions !"
			break


		# Draw a waiting time
		t.append(t[-1] + np.random.exponential(1./np.sum(rates)))


		# Update the state space
		trans = np.where(np.random.uniform() < np.cumsum(rates / np.sum(rates)))[0][0]
		model.X += model.transition[:, trans]


		# If we're tracking, keep track of the transition
		if track :
			tracked_trans_array[trans, tcount] = 1
			tcount += 1
			if tcount >= tracked_trans_array.shape[1] :
				tracked_trans_array = np.hstack((tracked_trans_array, np.zeros((model.N_events,randsize))))

		
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
		if not silent :
			helpers.progBarUpdate(t[-2:], tmax)


	# Reset state space
	if not propagate :
		model.X = np.array([model.initconds[x] for x in model.states], dtype=int)

	if track :
		return (t, trace, tracked_trans_array)
	else :
		return (t, trace)












def tauLeap(model, tmax, tau=1, track=False, silent=False, propagate=False, **kwargs) :

	# Initialise
	if not propagate :
		model.build(silent=True) # initialise model

	t = np.arange(0,tmax,tau)
	trace = np.zeros((np.ceil(float(tmax)/tau),len(model.X)))
	trace[0,:] = model.X[:]
	rates = np.zeros(model.N_events)
	tracking_idx = -1;

	# Start the progress bar
	if not silent :
		helpers.progBarStart()

	if track:
		tracked_trans_array = np.zeros((model.N_events,int(tmax/tau)))
		counter = 0

	cappedEvents = [np.where(model.transition[:, i] == -1)[0] for i in range(model.N_events)] # reaction takes one away from here


	# Continue until we hit tmax
	#while t[-1] < tmax :
	for idx, time in enumerate(t[:-1]):

		# Compute a rates vector 
		rates = [rate(model.X, time) for rate in model.rates]

		assert (np.array(rates) < 0).sum() == 0, "Negative rates found : %s" % rates

		# Determine which events occurred after ensuring that there's 
		# a valid transition, and update the state space
		if np.sum(rates) <= 0 :
			if not silent :
				print "Stopping early - no valid transitions !"
			trace = np.delete(trace,range(idx+1,int(tmax/tau)+1),0)
			t = np.delete(t,range(idx+1,int(tmax/tau)+1),0)
			if track:
				tracked_trans_array = np.delete(tracked_trans_array,range(idx+1,int(tmax/tau)+1),1)
			break

		# Correct so things don't go negative :		
		maxEvents = np.array([(model.X[i] if len(i) == 1 else np.inf) for i in cappedEvents]).flatten()

		# Determine the number of times each transition happens in tau time
		estEvents = np.array([np.random.poisson(rate * tau) for rate in rates], dtype=int)
		doneEvents = np.min((maxEvents, estEvents), axis=0).astype(int)


		# Increase time
		# if there's at least one reaction but we can't do them all
		if (doneEvents != estEvents).all() and np.sum(estEvents) > 0 :
			t[idx+1] = t[idx] + tau * float(np.sum(doneEvents)) / np.sum(estEvents)
		else :
			t[idx+1] = t[idx] + tau

		
		# Record tracked reactions
		if track :
			tracked_trans_array[:,idx] = doneEvents

		model.X += np.sum(model.transition * doneEvents, axis=1).astype(int)



		assert (model.X < 0).sum() == 0, "Negative state space ! Aborting."


		# Append new state space to trace
		trace[idx+1,:] = model.X


		# Update progress bar
		if not silent :
			helpers.progBarUpdate(t[idx:idx+1], len(t))


	# Reset state space
	if not propagate :
		model.X = np.array([model.initconds[x] for x in model.states], dtype=int)
	
	if track :
		return (t, trace, tracked_trans_array)
	else :
		return (t, trace)






