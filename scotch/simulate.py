# Simulation algorithms
import numpy as np
import helpers
from copy import copy, deepcopy



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
	trace = []
	trace.append(model.X[:].astype(int))

	# Preallocate array of tracked reactions
	if track :
		tracked_trans_array = []

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
				print("No more possible events, stopping early !")
			out = [t, np.array(trace)]
			if track :
				out.append(np.array(tracked_trans_array))
			return out

		# Draw a waiting time
		t.append(t[-1] + np.random.exponential(1./np.sum(rates)))

		# Select which transition occurs
		trans = np.where(np.random.uniform() < \
			np.cumsum(rates / np.sum(rates)))[0][0]

		# Update the state space
		model.X += model.transition[:, trans].astype(int)



		# If we're tracking, keep track of the transition
		if track :
			currentevent = np.zeros(model.N_events)
			currentevent[trans] = 1
			tracked_trans_array.append(currentevent)
			"""
			tracked_trans_array[trans, tcount] = 1
			tcount += 1
			if tcount >= tracked_trans_array.shape[1] :
				tracked_trans_array = np.hstack((tracked_trans_array, \
										np.zeros((model.N_events,randsize))))
			"""


		# At the end of randsize iterations, update randsize "adaptively"
		rcount += 1
		if rcount == randsize :
			rcount = 0
			randsize = max(1000, randsize * tmax / (tlast - t[-1]) - 1)
			rand = np.random.uniform(size=randsize)
			tlast = t[-1]



		# Append new state space to trace
		trace.append(list(model.X))


		# Update progress bar
		if not silent :
			helpers.progBarUpdate(t[-2:], tmax)


	# Termination #############################################################

	# Reset state space
	if not propagate :
		model.X = np.array([model.initconds[x] for x in model.states],
					dtype=int)

	# Return
	out = [t, np.array(trace)]
	if track :
		out.append(np.array(tracked_trans_array))

	return out









def tauLeap(model, tmax, tau=1, track=False, silent=False, propagate=False, noNegStatesAllowed = True, **kwargs) :

	# Initialisation ##########################################################

	# If user requested to propagate old results, don't build the model
	if not propagate :
		model.build(silent=True) # initialise model

	# Time array
	t = [0]

	# Initialise the trace
	trace = []
	trace.append(model.X[:].astype(int))

	# Timestep and tracking indices
	idx = 0

	# Start the progress bar
	if not silent :
		helpers.progBarStart()

	# Array of tracked reactions
	if track :
		tracked_trans_array = []#np.zeros((model.N_events,1)) #int(tmax/tau)))

	

	# Simulation loop #########################################################
	while t[-1] < tmax :

		# Compute a rates vector
		rates = [rate(model.X, t[-1]) for rate in model.rates]

		# Ensure all rates are valid
		if np.any(np.array(rates) < 0) :
			print(t[-1])
			print(rates)
			print(model.X)
			raise helpers.SimulationError("Negative rates found.")

		 # Ensure there are possible events to continue with
		if not np.any(np.array(rates) > 0) :
			if not silent :
				print("No more possible events, stopping early !")
			# Return
			out = [t, np.array(trace)]
			if track :
				out.append(np.array(tracked_trans_array))
			return out

		#Estimate the total number of events per transition
		estEvents = np.array([np.random.poisson(rate * tau) \
           for rate in rates], dtype=int)

		# Calculate transitions by statespace
		#tempTransitions_array = model.transition * estEvents

		# Create array of state space values to test against transitions
		#tempStateSpace = np.tile(model.X.reshape([model.N_states,1]), model.N_events)

		# Calculate net transitions by statespace
		tempTransitions = np.sum(model.transition * estEvents, axis=1).astype(int) 

		# Calculate negative transitions by statespace
		negTransitions = deepcopy(model.transition)
		negTransitions[model.transition>=0] =0 
		tempNegTransitions = np.sum(negTransitions * estEvents, axis=1).astype(int)

		# If tracking is on, check if there are any total negative transitions that go below the number
		# individuals in the statespace 
		if track :
			if noNegStatesAllowed & np.any(model.X + tempNegTransitions <0) :
				# create blank new transitions vector
				tempNewNegTransitions = np.zeros(model.N_states)
				#create new Events vector
				newEvents = np.zeros(model.N_events)
				# initiate tempEvents vector as estEvents
				tempEvents = deepcopy(estEvents)
				while np.all(model.X + tempNewNegTransitions >0) :
					#randomly pick an event from est Events
					newEventIdx = np.random.choice(model.N_events,None,True, tempEvents.astype(float)/np.sum(tempEvents))
					newEvents[newEventIdx] +=1
					tempEvents[newEventIdx]-=1
					#create vector of new negative transitions
					tempNewNegTransitions = np.sum(negTransitions * newEvents, axis=1).astype(int)
				diff = estEvents-newEvents
				reductionRatio = min(1-diff[diff>0]/estEvents[diff>0])
				#reductionRatio = max(newEvents/estEvents)
				model.X += np.sum(model.transition*newEvents, axis=1).astype(int)
				t.append(t[idx]+reductionRatio*tau)
				tracked_trans_array.append(newEvents)
			else :
				model.X += np.sum(model.transition*estEvents, axis=1).astype(int)
				t.append(t[idx]+tau)
				tracked_trans_array.append(estEvents)
		else :
			#Check if negative states exist and if they are allowed
			if noNegStatesAllowed & np.any(model.X + tempTransitions < 0) :
				#if negative states exist but are not allowed, find where they are                  
				tempNewModelStates =model.X + tempTransitions
				negidx= np.where(tempNewModelStates<0)
				#calculate ratio by which to reduce all transitions (max ratio of differences in events)
				reductionRatio = min(1-tempNewModelStates[negidx]/tempTransitions[negidx])
				#Adjust number of events done down by ratio
				estEvents_new = reductionRatio*estEvents
				# Update the state space
				model.X += np.sum(model.transition * estEvents_new, axis=1).astype(int)
				#update t by adjusted tau
				t.append(t[idx] + tau * reductionRatio)
			else :
			# Otherwise, add a full tau increment to the time array
				t.append(t[idx] + tau)
				# Update the state space
				model.X += np.sum(model.transition * estEvents, axis=1).astype(int)



					
		#check for negative
		# randomly until go negative -- keep track of new events vs est events -- that is ratio

		
		# #check if there are negative transitions
		# # check it total number of negative transitions goes below 0 
		# if noNegStatesAllowed & np.any((tempStateSpace + tempTransitions_array )<0) :
		# 	#if negative states exist but are not allowed, find where they are                  
		# 	tempNewStateSpaceChanges = (tempStateSpace+tempTransitions_array)
		# 	negidx = np.where(tempNewStateSpaceChanges <0) 
		# 	#calculate ratio by which to reduce all transitions (max ratio of differences in events)
		# 	reductionRatio = min(1-tempNewStateSpaceChanges[negidx]/tempTransitions_array[negidx])
		# 	#Adjust number of events done down by ratio
		# 	estEvents_new = reductionRatio*estEvents
		# 	# Update the state space
		# 	model.X += np.sum(model.transition * estEvents_new, axis=1).astype(int)

		# 	if track :
		# 		tracked_trans_array.append(estEvents_new)
		# 		print("time idx is")
		# 		print(idx)
		# 		print("time is")
		# 		print(t[idx])
		# 		print("estEvents_new are")
		# 		print(estEvents_new)
		# 		print("time idx is")
		# 		print(idx)
		# 		print("time is")
		# 		print(t[idx])
		# 	#update t by adjusted tau
		# 	t.append(t[idx] + tau * reductionRatio)
		# else :
		# # Otherwise, add a full tau increment to the time array
		# 	t.append(t[idx] + tau)
		# 	if track :
		# 		tracked_trans_array.append(estEvents)
		# 		print("time idx is")
		# 		print(idx)
		# 		print("time is")
		# 		print(t[idx])
		# 		print("estEvents are")
		# 		print(estEvents)

		# 	# Update the state space
		# 	model.X += np.sum(model.transition * estEvents, axis=1).astype(int)
		
			
		
		# Append new state space to trace, increment timestep index
		idx += 1
		trace.append(list(model.X))

		# Update progress bar
		if not silent :
			helpers.progBarUpdate(t[idx:(idx+1)],len(t))

		# Record tracked reactions
		#if track :
		#	tracked_trans_array.append(estEvents)
		


	# Termination #############################################################

	# Reset state space unless the user wants to carry it forward
	if not propagate :
		model.X = np.array([model.initconds[x] for x in model.states], dtype=int)


	# Return
	out = [t, np.array(trace)]
	if track :
		out.append(np.array(tracked_trans_array))

	return out

#  OLD TAU LEAP HERE JUST IN CASE
#   def tauLeap(model, tmax, tau=1, track=False, silent=False, propagate=False, **kwargs) :

#   # Initialisation ##########################################################

#   # If user requested to propagate old results, don't build the model
#   if not propagate :
#       model.build(silent=True) # initialise model

#   # Time array
#   t = [0]

#   # Initialise the trace
#   trace = []
#   trace.append(model.X[:].astype(int))

#   # Timestep and tracking indices
#   idx = 0

#   # Start the progress bar
#   if not silent :
#       helpers.progBarStart()

#   # Array of tracked reactions
#   if track :
#       tracked_trans_array = []#np.zeros((model.N_events,1)) #int(tmax/tau)))

#   # Which transitions need to be capped ?
#   cappedEvents = -(model.transition * (model.transition < 0))




#   # Simulation loop #########################################################
#   while t[-1] < tmax :

#       # Compute a rates vector
#       rates = [rate(model.X, t[-1]) for rate in model.rates]

#       # Ensure all rates are valid
#       if np.any(np.array(rates) < 0) :
#           print(t[-1])
#           print(rates)
#           print(model.X)
#           raise helpers.SimulationError("Negative rates found.")

#       # Ensure there are possible events to continue with
#       if not np.any(np.array(rates) > 0) :
#           if not silent :
#               print "No more possible events, stopping early !"
#           # Return
#           out = [t, np.array(trace)]
#           if track :
#               out.append(np.array(tracked_trans_array))
#           return out




#       # Estimate the total number of events per transition
#       estEvents = np.array([np.random.poisson(rate * tau) \
#           for rate in rates], dtype=int)


#       # Find the maximum number of removals from a state that can occur
#       maxEvents = (cappedEvents * estEvents).sum(1)

#       # If we want more removals than are possible from that state :
#       if np.any((model.X - maxEvents) < 0) :

#           # Find the largest discrepancy
#           discrepancy = np.argmin(model.X - maxEvents)

#           # Adjust done events
#           estEvents = np.floor(estEvents * \
#               model.X[discrepancy] / float(maxEvents[discrepancy])).astype(int)

#       else :
#           # Otherwise, there's no discrepancy between our estimate and the possible max
#           discrepancy = -1

# #problem is around here -- need to check for all of the places where there are too many events

#       # If there's at least one event but we can't do them all :
#       if (discrepancy > -1) and np.sum(estEvents) > 0 :
#           # Then we do fewer events, so adjust time increment accordingly
#           t.append(t[idx] + tau * model.X[discrepancy] / float(maxEvents[discrepancy]))
#       else :
#           # Otherwise, add a full tau increment to the time array
#           t.append(t[idx] + tau)



#       # Update the state space
#       model.X += np.sum(model.transition * estEvents, axis=1).astype(int)

#       # Append new state space to trace, increment timestep index
#       idx += 1
#       trace.append(list(model.X))


#       # Record tracked reactions
#       if track :
#           tracked_trans_array.append(estEvents)
#           """
#           if idx >= tracked_trans_array.shape[1] :
#               addingEvents = np.expand_dims(estEvents, axis=1)
#               tracked_trans_array = np.hstack((tracked_trans_array, addingEvents))
#           else :
#               tracked_trans_array[:, idx] = estEvents
#           """



#       # Update progress bar
#       if not silent :
#           helpers.progBarUpdate(t[idx:(idx+1)], len(t))




#   # Termination #############################################################

#   # Reset state space unless the user wants to carry it forward
#   if not propagate :
#       model.X = np.array([model.initconds[x] for x in model.states], dtype=int)


#   # Return
#   out = [t, np.array(trace)]
#   if track :
#       out.append(np.array(tracked_trans_array))

#   return out

