# Simulation algorithms
import numpy as np
import helpers








# Gillespie algorithm
def gillespie(model, tmax, track=False, incremental=False) :

	# Initialise
	t = [0]
	model.build(silent=True) # initialise model
	trace = model.X[:]
	rates = np.zeros(model.N_events)

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

	# Pre-allocate matrix of tracked reactions
	if track:
		tracked_trans_array = np.zeros((model.N_events,randsize))
		tcount = 0

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
		if track :
			tracked_trans_array[trans, tcount] = 1
			tcount += 1
			if tcount >= tracked_trans_array.shape[1] :
				tracked_trans_array = np.hstack((tracked_trans_array, np.zeros((model.N_events,randsize))))
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

	if track :
		return (t, trace, tracked_trans_array)
	else :
		return (t, trace)




def tauLeap(model, tmax, tau=1, track=False, incremental=False) :

	# Initialise
	model.build(silent=True) # initialise model
	t = np.arange(0,tmax,tau)
	trace = np.zeros((int(tmax/tau),len(model.X)))
	trace[0,:] = model.X[:]
	rates = np.zeros(model.N_events)
	tracking_idx = -1;

	# Start the progress bar
	helpers.progBarStart()

	if track:
		tracked_trans_array = np.zeros((model.N_events,int(tmax/tau)))
		counter = 0
		#print int(tmax/tau)


	"""
	# If we're tracking individuals, generate IDs for everyone
	if track :
		maxID = 0
		individuals = {}
		for i, state in enumerate(model.states) :
			individuals[state] = range(maxID, maxID + model.X[i])
			maxID += model.X[i]
	"""

	cappedEvents = [np.where(model.transition[:, i] == -1)[0] for i in range(model.N_events)] # reaction takes one away from here


	# Continue until we hit tmax
	#while t[-1] < tmax :
	for idx, time in enumerate(t[:-1]):

		# Compute a rates vector 
		rates = [rate(model.X) for rate in model.rates]

		assert (np.array(rates) < 0).sum() == 0, "Negative rates, you die now. % s" % rates

		# Determine which events occurred after ensuring that there's 
		# a valid transition, and update the state space
		if np.sum(rates) <= 0 :
			print "Stopping early - no valid transitions !"
			trace = np.delete(trace,range(idx,int(tmax/tau)+1),0)
			t = np.delete(t,range(idx,int(tmax/tau)+1),0)
			tracked_trans_array = np.delete(tracked_trans_array,range(idx,int(tmax/tau)+1),1)
			break

		# Correct so things don't go negative :		
		maxEvents = np.array([model.X[i] if len(i) == 1 else np.inf for i in cappedEvents], dtype=int)[:, 0]

		# Determine the number of times each transition happens in tau time
		estEvents = np.array([np.random.poisson(rate * tau) for rate in rates], dtype=int)
		doneEvents = np.min((maxEvents, estEvents), axis=0).astype(int)

		#if not (doneEvents != estEvents).all() :
		#	print "Some events could not take place due to small state variable."
		#	print "Perhaps tau is too large."

		# Increase time
		# if there's at least one reaction but we can't do them all
		if (doneEvents != estEvents).all() and np.sum(estEvents) > 0 :
			t[idx+1] = t[idx] + tau * float(np.sum(doneEvents)) / np.sum(estEvents)
		else :
			t[idx+1] = t[idx] + tau

		
		#record tracked reactions
		if track :
			tracked_trans_array[:,idx] = doneEvents
			
			# if counter >= tracked_trans_array.shape[1] :
			#  	tracked_trans_array = np.hstack((tracked_trans_array, np.zeros((model.N_events,1))))

		#print model.reactions
		#print doneReactions*model.transition
		#print np.sum(model.transition * doneReactions, axis=1)


		# # Check if model is tracking states
		# if model.tracked_states != None :
		# 	if int(t[-1]) > tracking_idx:
		# 		tracking_idx+=1
		# 		tracked_IDs = {}
		# 	# set up vectors for states if t =0
		# 		for s in model.tracked_states :
		# 			tracked_IDs[s] = []
		# 	# set up temporary dictionary to count reactions for each state
		# 	temp_count_dict = {}
		# 	for s in model.tracked_states :

		# 		temp_count_dict[s].append

		# Check if model is tracking reactions
		

			








		# print "State space", model.X
		# print "Done events", doneEvents
		# print "State Space Change", np.sum(model.transition * doneEvents, axis=1)
		# print "Est", estEvents
		# print "Max events", maxEvents
		# Update the state space
		model.X += np.sum(model.transition * doneEvents, axis=1).astype(int)



		assert (model.X < 0).sum() == 0, "Negative state space, you DIE NAO"


		# Append new state space to trace
		#trace = np.vstack((trace, model.X))
		trace[idx+1,:] = model.X


		# Update progress bar
		helpers.progBarUpdate(t[idx:idx+1], len(t))


	# Reset state space
	model.X = np.array([model.initconds[x] for x in model.states], dtype=int)
	if track :
		return (t, trace, tracked_trans_array)
	else :
		return (t, trace)




# def count_tracked(tracked_state,  model, doneReactions) :
# 	for idx, r in enumerate(model.reactions):
# 		if r[1] == tracked_state :
# 			count = doneReactions[idx]
# 	return count

# 	# PROBLEM :
# 	# Max reactions should take into account total outwards stream, not just per reaction




# def track_reactions(model, trackAll = True):
# 	if trackAll == False:
# 		print "Would you like to track any reactions? (y/n)"
# 		reaction_tracker_ind = raw_input()
# 		if reaction_tracker_ind == "y" :
# 			print model
# 			print "Which reactions would you like to track? (enter Reaction Numbers separated by commas)"				
# 			incorrectReactions = True
# 			while incorrectReactions == True:
# 				num_tracked_trans = raw_input().split(",")					
# 				int_tracked_trans = [int(x) for x in num_tracked_trans]
# 				#print range(len(model.reactions))
# 				checkset = [x for x in int_tracked_trans if x not in range(len(model.reactions))]
# 				if checkset == []:
# 						incorrectReactions = False
# 				else:
# 					print ("Error: %s  not valid reaction number(s)" % checkset)
# 					print ("Please re-enter reaction numbers") 



# 			#print incorrectReactions
# 			model.tracked_trans = [model.reactions[x] for x in int_tracked_trans] 
# 			#print model.tracked_trans
# 			#generate tracked states from transitions					
# 			model.tracked_states = []
# 			for t in model.tracked_trans :
# 				for t2 in t :
# 					if (t2 in model.states and t2 not in model.tracked_states):
# 						model.tracked_states.append(t2)
# 		else :
# 			print "Would you like to track any states? (y/n)"
# 			state_tracker_ind = raw_input()

# 			if state_tracker_ind == "y":
# 				print "Which states would you like to track? (Enter state numbers separated by commas)"
# 				for idx,state in enumerate(model.states):
# 					print ("Number %s: %s" %(idx, state))
# 				incorrectStates = True
# 				while  incorrectStates == True:
# 					num_tracked_states = raw_input().split(",")
# 					int_tracked_states = [int(x) for x in num_tracked_states]
# 					checkset = [x for x in int_tracked_states if x not in range(len(model.states))]
# 					if checkset == []:
# 						incorrectStates = False
# 					else:
# 						print ("Error: %s  not valid state number(s)" % checkset)
# 						print ("Please re-enter state numbers")

# 				model.tracked_states = [model.states[x] for x in int_tracked_states] 
# 	else:
# 		model.tracked_trans = model.reactions
# 		model.tracked_states = model.states







def sample(model, tmax, algorithm=gillespie) :
	pass