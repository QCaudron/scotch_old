# Simulation algorithms
import numpy as np
import helpers




# Gillespie algorithm
def gillespie(model, tmax, track=False, silent=False, propagate=False, **kwargs) :

	# Initialise ##############################################################

	# Generate this many random uniforms at once, for speed
	randsize = 1000

	# Timestep at which random numbers were last updated
	tlast = 0

	# Time array
	t = [0]

	# If user requested to propagate old results, don't build the model
	if not propagate :
		model.build(silent=True) # initialise model

	# Initialise the trace
	trace = model.X[:]

	# Preallocate array of tracked reactions
	if track :
		tracked_trans_array = np.zeros((model.N_events,randsize))
		tcount = 0

	# Pregenerate some random numbers
	rand = np.random.uniform(size=1000)
	rcount = 0

	# Start the progress bar
	if not silent :
		helpers.progBarStart()




	# Simulation loop #########################################################
	while t[-1] < tmax :

		# Compute a rates vector
		rates = [rate(model.X, t[-1]) for rate in model.rates]

		# Ensure all rates are statistically valid
		if np.any(np.array(rates) < 0) :
			raise helpers.SimulationError("Negative rates found.")

		# Ensure there are possible events to continue with
		if not np.any(np.array(rates) > 0) :
			if not silent :
				print "No more possible events, stopping early !"
			return (t, trace) if not track else (t, trace, tracked_trans_array)

		# Draw a waiting time
		t.append(t[-1] + np.random.exponential(1./np.sum(rates)))

		# Select which transition occurs
		trans = np.where(np.random.uniform() < \
			np.cumsum(rates / np.sum(rates)))[0][0]

		# Update the state space
		model.X += model.transition[:, trans].astype(int)



		# If we're tracking, keep track of the transition
		if track :
			tracked_trans_array[trans, tcount] = 1
			tcount += 1
			if tcount >= tracked_trans_array.shape[1] :
				tracked_trans_array = np.hstack((tracked_trans_array, \
										np.zeros((model.N_events,randsize))))

		

		# At the end of randsize iterations, update randsize "adaptively"
		rcount += 1
		if rcount == randsize :
			rcount = 0
			randsize = max(1000, randsize * tmax / (tlast - t[-1]) - 1)
			rand = np.random.uniform(size=randsize)
			tlast = t[-1]


		
		# Append new state space to trace
		trace = np.vstack((trace, model.X)).astype(int)

		# Update progress bar
		if not silent :
			helpers.progBarUpdate(t[-2:], tmax)


	# Termination #############################################################

	# Reset state space
	if not propagate :
		model.X = np.array([model.initconds[x] for x in model.states], 
					dtype=int)

	# Return
	return (t, trace) if not track else (t, trace, tracked_trans_array)















def tauLeap(model, tmax, tau=1, track=False, silent=False, propagate=False, **kwargs) :

	# Initialisation ##########################################################

	# If user requested to propagate old results, don't build the model
	if not propagate :
		model.build(silent=True) # initialise model

	# Time array
	t = [0]

	# Initialise the trace
	trace = model.X[:]

	# Timestep and tracking indices
	idx = 0
	tracking_idx = -1;

	# Start the progress bar
	if not silent :
		helpers.progBarStart()

	# Preallocate array of tracked reactions
	if track :
		tracked_trans_array = np.zeros((model.N_events,int(tmax/tau)))
		counter = 0

	# Which transitions need to be capped ?
	cappedEvents = -(model.transition * (model.transition < 0))




	# Simulation loop #########################################################
	while t[-1] < tmax :
	
		# Compute a rates vector 
		rates = [rate(model.X, t[-1]) for rate in model.rates]

		# Ensure all rates are valid
		if np.any(np.array(rates) < 0) :
			raise helpers.SimulationError("Negative rates found.")

		# Ensure there are possible events to continue with
		if not np.any(np.array(rates) > 0) :
			if not silent :
				print "No more possible events, stopping early !"
			return (t, trace) if not track else (t, trace, tracked_trans_array)


		# What the hell was this madness ?
		# It's here for book-keeping until next update, but
		# serves no purpose... Too much caffeine ?!
		"""
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
		"""

		# Estimate the total number of events per transition
		estEvents = np.array([np.random.poisson(rate * tau) \
			for rate in rates], dtype=int)

		# Find the maximum number of removals from a state that can occur
		maxEvents = (cappedEvents * estEvents).sum(1)

		# If we want more removals than are possible from that state :
		if np.any((model.X - maxEvents) < 0) :

			# Find the largest discrepancy
			discrepancy = np.argmin(model.X - maxEvents)

			# Adjust done events
			estEvents = np.floor(estEvents * \
				model.X[discrepancy] / float(maxEvents[discrepancy])).astype(int)

		else :
			# Otherwise, there's no discrepancy between our estimate and the possible max
			discrepancy = -1



		# If there's at least one event but we can't do them all :
		if (discrepancy > -1) and np.sum(estEvents) > 0 :
			# Then we do fewer events, so adjust time increment accordingly
			t.append(t[idx] + tau * model.X[discrepancy] / float(maxEvents[discrepancy]))
		else :
			# Otherwise, add a full tau increment to the time array
			t.append(t[idx] + tau)



		# Update the state space
		model.X += np.sum(model.transition * estEvents, axis=1).astype(int)

		# Append new state space to trace, increment timestep index
		idx += 1
		trace = np.vstack((trace, model.X))

		

		
		# Record tracked reactions
		if track :
			tracked_trans_array[:, idx] = estEvents

		# Update progress bar
		if not silent :
			helpers.progBarUpdate(t[idx:(idx+1)], len(t))




	# Termination #############################################################

	# Reset state space unless the user wants to carry it forward
	if not propagate :
		model.X = np.array([model.initconds[x] for x in model.states], dtype=int)
	
	# Return
	return (t, trace, tracked_trans_array) if track else (t, trace)






