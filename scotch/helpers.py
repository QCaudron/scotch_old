import sys
import numpy as np




# Required model fields
required = ["States",
			"Parameters",
			"InitialConditions",
			"Events"]




# Errors

class FileNotFound(Exception) :
	pass

class InvalidModel(Exception) :
	pass

class SimulationError(Exception) :
	pass










# Parse user-input

def parse(S, states_map=[], params=[], onlyStates=False) :

	# Buffer ( substrings between operators ), and parsed list
	buff = []
	out = []

    # Operators
	symbols = ["+", "-", "*", "/", "(", ")", "#"]
	operations = ["sin", "cos", "tan", "arcsin", "arccos", "arctan", # trigonometric
				  "sinh", "cosh", "tanh", "arcsinh", "arccosh", "arctanh", # hyperbolic
				  "ceil", "floor", "abs", # rounding
				  "exp", "log", "expm1", "log10", "log2", "log1p", # transcendental
				  "sinc", "sqrt", "square", "sign", # other
				  "pi"] # constants

	S = S.replace(" ", "") + "#"

	# For each character in the string to be parsed
	for s in S :

        # If it's an operator
		if s in symbols :

            # Generate a string from what's currently in the buffer
			buff = "".join(buff)

            # If it's a parameter, wrap it in ()
			if buff in params :
				if not onlyStates :
					out.append("(%s)" % parse(params[buff]))
				else :
					out.append("1.0")

            # Else, if it's a state variable, replace it with vector notation
			elif buff in states_map :
				out.append("float(X[%d])" % states_map[buff])

            # Else, it's a constant, cast as a float
			elif buff :
				out.append("float(%s)" % buff)

            # Don't forget the operator itself
			out.append(s)

            # And empty the buffer
			buff = []

        # Otherwise it's not an operator, append it to the buffer
		else :
			buff.append(s)

    # Remove trailing token
	out.remove("#")

	# Do some numpy stuffs
	out = "".join(out)
	for operation in operations :
		out = out.replace("float(%s)" % operation, "np.%s" % operation)

    # Return a string that should fit in eval()
	return out










def progBarStart(width=25) :

	sys.stdout.write("[%s]" % (" " * width))
	sys.stdout.flush()
	sys.stdout.write("\b" * (width+1))




def progBarUpdate(t, tmax, width=25) :

	if np.fmod(t[0] / float(tmax), 1./width) > np.fmod(t[-1] / float(tmax), 1./width) :
		sys.stdout.write("-")
		sys.stdout.flush()








# def trackIndividuals(model, tracking_array, t, keepIndividuals=False, trackActors=False, **kwargs) :

# 	# Initialize dictionary of arrays by state
# 	statesDict = {}
# 	for s in model.states :
# 		statesDict[s] = []



# 	# Input initial conditions
# 	lastID = 0

# 	for key in statesDict.keys() :
# 		if model.initconds[key] >0 :
# 			statesDict[key].append(range(lastID, lastID+model.initconds[key]))
# 			lastID += model.initconds[key]
# 		else :
# 			statesDict[key].append([])

# 	if trackActors :
# 		actorPairsDict = {}
# 		for x in model.events :
# 			actorPairsDict[x[0]] = []



# 	# Check if user wants to keep ids between states or not
# 	# do something about source and sink states
# 	if keepIndividuals:
# 		#Go through each time step
# 		for idx, val in enumerate(t[:-1]) :
# 			# print("Time is")
# 			# print(val)
# 			# reset matrix of number of IDs to move (number of events by number of states)
# 			numIDs_to_move = np.zeros((model.N_events, model.N_states))
# 			for idx2, val2 in enumerate(tracking_array[:,idx]) :
# 				#calculate how many transitions to do
# 				numIDs_to_move[idx2,:] = model.transition[:,idx2]*val2
# 			# print("numIDs_to_move is")
# 			# print(numIDs_to_move)


# 			# set up temporary list of ids in the latest timestep for each state
# 			temp_stateDict = [ list(statesDict[x][-1]) for x in model.states]
# 			if trackActors :
# 				#set up temporary list of actor pairs per timestep
# 				temp_actorPairsList = {i:[] for i in model.optional['actors'].keys()}

# 			# go through each event and move ids to/from appropriate states
# 			for idx2,item2 in enumerate(numIDs_to_move) :
# 				# check if there are actors
# 				eventActors = False
# 				if trackActors:
# 					if not (model.optional['actors'][model.events[idx2][0]] == '[]'):
# 						eventActors = True




# 				# go through each state in order and remove or add items
# 				# need to always take IDS from  losing state first
# 				# get IDs being taken away
# 				#first check if any additions without subtractions happen
# 				if all(i >=0 for i in item2) and not all(i == 0 for i in item2):
# 					#if so, generate new ids to add to state where things get added
# 					state_idx_add = np.where(item2 > 0)[0]
# 					for i in range(int(item2[state_idx_add])) :
# 						lastID +=1
# 						if trackActors and eventActors:

# 							#add pair of actors to temp dict
# 							#get random actor from actor class by
# 							#choosing random ID from corresponding temp_stateDict
# 							increment_actors_dict(model, temp_actorPairsList ,idx2, lastID,temp_stateDict)

# 				    	temp_stateDict[state_idx_add].append(lastID)
# 				elif all(i <=0 for i in item2) and not all(i == 0 for i in item2):
# 					# next, check if there are any events that are just removals
# 					state_idx_remove = np.where(item2 < 0)[0]
# 					num_items_to_move = item2[state_idx_remove]
# 					ids_to_move = []
# 					for i in np.random.choice(temp_stateDict[state_idx_remove],np.abs(num_items_to_move),replace=False) :
# 					    ids_to_move.append(i)
# 					    if trackActors and eventActors:

# 						#add pair of actors to temp dict
# 						#get random actor from actor class by
# 						#choosing random ID from corresponding temp_stateDict
# 							increment_actors_dict(model, temp_actorPairsList ,idx2, i, temp_stateDict)
# 							# print temp_actorPairsList

# 					    temp_stateDict[state_idx_remove].remove(i)
# 				elif not all(i == 0 for i in item2):
# 					#lastly, go through events where IDs move from one state to another
# 					state_idx_remove = np.where(item2 < 0)[0]
# 					num_items_to_move = item2[state_idx_remove]
# 					ids_to_move = []
# 					for i in np.random.choice(temp_stateDict[state_idx_remove],np.abs(num_items_to_move),replace=False) :
# 					    ids_to_move.append(i)
# 					    if trackActors and eventActors:

# 						#add pair of actors to temp dict
# 						#get random actor from actor class by
# 						#choosing random ID from corresponding temp_stateDict
# 							increment_actors_dict(model, temp_actorPairsList ,idx2, i, temp_stateDict)
# 							# print temp_actorPairsList

# 					    temp_stateDict[state_idx_remove].remove(i)
# 					#add IDs to state that gets incremented
# 					state_idx_add = np.where(item2 > 0)[0]
# 					for i in ids_to_move :
# 						temp_stateDict[state_idx_add].append(i)




# 			for idx3, item in enumerate(model.states) :
# 				statesDict[item].append(temp_stateDict[idx3])

# 			if trackActors:
# 				for item in model.events:
# 					actorPairsDict[item[0]].append(temp_actorPairsList[item[0]])


# 	else :
# 		for idx, val in enumerate(t[:-1]) :
# 			# print "time index is", idx
# 			numIDs_to_move = np.zeros((model.N_events, model.N_states))
# 			for idx2, val2 in enumerate(tracking_array[:,idx]) :
# 				#calculate how many transitions to do

# 				numIDs_to_move[idx2,:] = model.transition[:,idx2]*val2

# 			temp_stateDict = [ list(statesDict[x][-1]) for x in model.states]
# 			for idx2,item2 in enumerate(numIDs_to_move) :
# 				for idx3, item3 in enumerate(item2):
# 				     if item3 < 0 :

# 				         #remove
# 				         for i in np.random.choice(temp_stateDict[idx3],np.abs(item3),replace=False) :
# 				             # print "removed id is", i
# 				             temp_stateDict[idx3].remove(i)
# 				     elif item3 > 0 :
# 				         for i in range(int(item3)) :
# 				               lastID+=1
# 				               temp_stateDict[idx3].append(lastID)
# 				               if trackActors and eventActors:
# 									increment_actors_dict(model, temp_actorPairsList ,idx2, i, temp_stateDict)


# 			for idx, item in enumerate(model.states) :
# 				statesDict[item].append(temp_stateDict[idx])
# 				#go through temp dictionary of actor pairs and append the ones for this time step
# 			if trackActors and eventActors:
# 				for item in model.events:
# 					actorPairsDict[item[0]].append(temp_actorPairsList[item[0]])


#     #Sort IDs in statesDict
# 	for x in model.states:
# 		for y in statesDict[x]:
# 			y.sort()

# 	if trackActors:
# 		for x in model.events:
# 			for y in actorPairsDict[x[0]]:
# 				y.sort(key = lambda tup: (tup[0],tup[1]))
# 		return statesDict, actorPairsDict
# 	else :
# 		return statesDict








def add_actors_wizard(model) :

	actors = {};
	print "This wizard will help assign states as actors for each events"
	print "The states to choose from are", [x.encode('utf8') for x in model.states]
	for x in model.events :
		print "Enter actor for the following event (enter '[]' without quotes if no actor)\n",x[0].encode('utf8')
		temp_actor = raw_input().strip()
		while (temp_actor not in model.states and temp_actor != '[]')  :
			print "Please re-enter a valid state:"
			temp_actor = raw_input().strip()
		actors[x[0]] = temp_actor

	model.optional["actors"] = actors








def increment_actors_dict(model, temp_actorPairsDict,idx, acteeID,temp_stateDict) :

	tempActor = model.optional['actors'][model.events[idx][0]]
	if not (tempActor == '[]'):
		tempActorID = np.random.choice(temp_stateDict[model.states_map[tempActor]])

		temp_actorPairsDict[model.events[idx][0]].append((tempActorID,acteeID))



def trackIndividuals(model, tracking_array, t, keepIndividuals = False, trackActors = False, **kwargs) :
	# Initialize dictionary of arrays by state
	statesDict = {}
	for s in model.states :
		statesDict[s] = []

	#create waiting dictionaries for ids to remove and ids to add
	# for s in model.states :
	# 	tempIDsToRemove[s] = []
	# for s in model.states :
	# 	tempIDsToAdd[s] = []

	# Input initial conditions
	lastID = 0

	#Check if there is a patch2states_list
	if 'patch2states_list' in kwargs.keys():
		patch2states_list = kwargs['patch2states_list']
	else :
		patch2states_list = []

	# read initial IDs into main patch state
	for key in statesDict.keys() :
		if model.initconds[key] >0 and key not in patch2states_list :
			statesDict[key].append(range(lastID, lastID+model.initconds[key]))
			lastID += model.initconds[key]
		elif model.initconds[key] >0 and key in patch2states_list :
		#put negative IDs in second patch
			statesDict[key].append(range(-lastID, -(lastID+model.initconds[key]),-1))
			lastID += model.initconds[key]
		else:
			statesDict[key].append([])



	if trackActors :
		actorPairsDict = {}
		for x in model.events :
			actorPairsDict[x[0]] = []



	# Check if user wants to keep ids between states or not
	# keep IDS to delete from each state until the end of the time step
	#and delete them at the start of the next timestep
	if keepIndividuals:
		#Go through each time step
		for idx, val in enumerate(t[:-1]) :
			# print("Time is")
			# print(val)
			# print("Time index is")
			# print(idx)
			# reset matrix of number of IDs to move (number of events by number of states)
			numIDs_to_move = np.zeros((model.N_events, model.N_states))
			for idx2, val2 in enumerate(tracking_array[idx,:]) :
				#calculate how many transitions to do
				numIDs_to_move[idx2,:] = model.transition[:,idx2]*val2
			# print("numIDs_to_move is")
			# print(numIDs_to_move)


			# set up temporary list of ids in the latest timestep for each state
			temp_stateDict = [ list(statesDict[x][-1]) for x in model.states]
			# set up list of ids that can be removed
			tempIDsToRemove = [ list(statesDict[x][-1]) for x in model.states]
			# set/reset list of IDs to add to each state
			tempIDsToAdd = [ [] for  x in range(model.N_states)] #{i:[] for i in model.states}
			#remove the IDs
			if trackActors :
				#set up temporary list of actor pairs per timestep
				temp_actorPairsList = {i:[] for i in model.optional['actors'].keys()}

			# go through each event and move ids to/from appropriate states
			for idx2,item2 in enumerate(numIDs_to_move) :
				# idx2 is the index of the event, while item2 is the number of times it
				# check if there are actors
				eventActors = False
				if trackActors:
					if not (model.optional['actors'][model.events[idx2][0]] == '[]'):
						eventActors = True




				# go through each state in order and remove or add items
				# need to always take IDS from  losing state first
				# get IDs being taken away
				#first check if any subtractions happen
				if all(i >=0 for i in item2) and not all(i == 0 for i in item2):
					#if not, generate new ids to add to state where things get added
					state_idx_add = np.where(item2 > 0)[0]
					for i in range(int(item2[state_idx_add])) :
						# use absolute value to capture incrementing negative IDs
						lastID = abs(lastID)+ 1
						if state_idx_add in [model.states_map[x] for x in patch2states]:
							lastID = -lastID
						if trackActors and eventActors:

							#add pair of actors to temp dict
							#get random actor from actor class by
							#choosing random ID from corresponding temp_stateDict
							increment_actors_dict(model, temp_actorPairsList ,idx2, lastID,temp_stateDict)

				    	tempIDsToAdd[state_idx_add].append(lastID)
				elif all(i <=0 for i in item2) and not all(i == 0 for i in item2):
					# next, check if there are any events that are just removals
					state_idx_remove = np.where(item2 < 0)[0]
					num_items_to_move = item2[state_idx_remove]
					#ids_to_move = []
					for i in np.random.choice(tempIDsToRemove[state_idx_remove],np.abs(num_items_to_move),replace=False) :
					    #ids_to_move.append(i)
					    if trackActors and eventActors:

						#add pair of actors to temp dict
						#get random actor from actor class by
						#choosing random ID from corresponding temp_stateDict
							increment_actors_dict(model, temp_actorPairsList ,idx2, i, temp_stateDict)
							# print temp_actorPairsList

					    tempIDsToRemove[state_idx_remove].remove(i)
				elif not all(i == 0 for i in item2):
					#lastly, go through events where IDs move from one state to another
					state_idx_remove = np.where(item2 < 0)[0]
					num_items_to_move = item2[state_idx_remove]
					ids_to_move = []
					# print "Event is " + model.events[idx2][0]
					# print "state_idx_remove is %d" %state_idx_remove
					# print "number of IDs to move is %d" %num_items_to_move
					# print "length of temp_stateDict[state_idx_remove] is " 
					# print len(temp_stateDict[state_idx_remove])
					# print "length of tempIDsToRemove[state_idx_remove] is " 
					# print len(tempIDsToRemove[state_idx_remove])
					


					for i in np.random.choice(tempIDsToRemove[state_idx_remove],np.abs(num_items_to_move),replace=False) :
					    ids_to_move.append(i)
					    if trackActors and eventActors:

						#add pair of actors to temp dict
						#get random actor from actor class by
						#choosing random ID from corresponding temp_stateDict
							increment_actors_dict(model, temp_actorPairsList ,idx2, i, temp_stateDict)
							# print temp_actorPairsList

					    tempIDsToRemove[state_idx_remove].remove(i)
					# print "new length of tempIDsToRemove[state_idx_remove] is " 
					# print len(tempIDsToRemove[state_idx_remove])

					#add IDs to state that gets incremented
					state_idx_add = np.where(item2 > 0)[0]
					for i in ids_to_move :
						tempIDsToAdd[state_idx_add].append(i)



			# Update statesDict to reflect the changes made during the transition,
			# print "Made it to incrementing step for timestep %d" %idx
			for idx3, item in enumerate(model.states) :			
				#temp_stateDict[idx3] = tempIDsToRemove[idx3] + tempIDsToAdd[idx3]
				#statesDict[item].append(temp_stateDict[idx3])
				statesDict[item].append(list(tempIDsToRemove[idx3] + tempIDsToAdd[idx3]))

			if trackActors:
				for item in model.events:
					actorPairsDict[item[0]].append(temp_actorPairsList[item[0]])


	else : #if new ids are being generated at each event
		for idx, val in enumerate(t[:-1]) :
			numIDs_to_move = np.zeros((model.N_events, model.N_states))
			for idx2, val2 in enumerate(tracking_array[:,idx]) :
				#calculate how many transitions to do

				numIDs_to_move[idx2,:] = model.transition[:,idx2]*val2
			# set up snapshot list of IDs at previous timestep
			temp_stateDict = [ list(statesDict[x][-1]) for x in model.states]
			# set up list of ids that can be removed
			tempIDsToRemove = [ list(statesDict[x][-1]) for x in model.states]
			# set/reset list of IDs to add to each state
			tempIDsToAdd = [ [] for  x in range(model.N_states)] #{i:[] for i in model.states}

			for idx2,item2 in enumerate(numIDs_to_move) :
				for idx3, item3 in enumerate(item2):
				     if item3 < 0 :

				         #remove
				         for i in np.random.choice(temp_stateDict[idx3],np.abs(item3),replace=False) :
				             # print "removed id is", i
				             temp_stateDict[idx3].remove(i)
				     elif item3 > 0 :
				         for i in range(int(item3)) :
				         	#use absolute value to capture negative IDs
				               lastID = abs(lastID) +1
				               if idx3 in [model.states_map[x] for x in patch2states]:
				               		lastID = -lastID
				               temp_stateDict[idx3].append(lastID)
				               if trackActors and eventActors:
									increment_actors_dict(model, temp_actorPairsList ,idx2, i, temp_stateDict)


			for idx, item in enumerate(model.states) :
				statesDict[item].append(temp_stateDict[idx])
				#go through temp dictionary of actor pairs and append the ones for this time step
			if trackActors and eventActors:
				for item in model.events:
					actorPairsDict[item[0]].append(temp_actorPairsList[item[0]])


    #Sort IDs in statesDict
	for x in model.states:
		for y in statesDict[x]:
			y.sort(key = abs)

	if trackActors:
		for x in model.events:
			for y in actorPairsDict[x[0]]:
				y.sort(key = lambda tup: (abs(tup[0]),abs(tup[1])))
		return statesDict, actorPairsDict
	else :
		return statesDict


# Old, buggy trackIndividuals

# def trackIndividuals(model, tracking_array, t, keepIndividuals = False, trackActors = False, **kwargs) :
# 	# Initialize dictionary of arrays by state
# 	statesDict = {}
# 	for s in model.states :
# 		statesDict[s] = []

# 	#create waiting dictionary for states to remove
# 	#for s in model.states :
# 	#	tempIDsToRemove[s] = []

# 	# Input initial conditions
# 	lastID = 0

# 	#Check if there is a patch2states_list
# 	if 'patch2states_list' in kwargs.keys():
# 		patch2states_list = kwargs['patch2states_list']
# 	else :
# 		patch2states_list = []

# 	# read initial IDs into main patch state
# 	for key in statesDict.keys() :
# 		if model.initconds[key] >0 and key not in patch2states_list :
# 			statesDict[key].append(range(lastID, lastID+model.initconds[key]))
# 			lastID += model.initconds[key]
# 		elif model.initconds[key] >0 and key in patch2states_list :
# 		#put negative IDs in second patch
# 			statesDict[key].append(range(-lastID, -(lastID+model.initconds[key]),-1))
# 			lastID += model.initconds[key]
# 		else:
# 			statesDict[key].append([])



# 	if trackActors :
# 		actorPairsDict = {}
# 		for x in model.events :
# 			actorPairsDict[x[0]] = []



# 	# Check if user wants to keep ids between states or not
# 	# keep IDS to delete from each state until the end of the time step
# 	#and delete them at the start of the next timestep
# 	if keepIndividuals:
# 		#Go through each time step
# 		for idx, val in enumerate(t[:-1]) :
# 			# print("Time is")
# 			# print(val)
# 			# reset matrix of number of IDs to move (number of events by number of states)
# 			numIDs_to_move = np.zeros((model.N_events, model.N_states))
# 			for idx2, val2 in enumerate(tracking_array[:,idx]) :
# 				#calculate how many transitions to do
# 				numIDs_to_move[idx2,:] = model.transition[:,idx2]*val2
# 			# print("numIDs_to_move is")
# 			# print(numIDs_to_move)


# 			# set up temporary list of ids in the latest timestep for each state
# 			temp_stateDict = [ list(statesDict[x][-1]) for x in model.states]
# 			#remove the IDs
# 			if trackActors :
# 				#set up temporary list of actor pairs per timestep
# 				temp_actorPairsList = {i:[] for i in model.optional['actors'].keys()}

# 			# go through each event and move ids to/from appropriate states
# 			for idx2,item2 in enumerate(numIDs_to_move) :
# 				# check if there are actors
# 				eventActors = False
# 				if trackActors:
# 					if not (model.optional['actors'][model.events[idx2][0]] == '[]'):
# 						eventActors = True




# 				# go through each state in order and remove or add items
# 				# need to always take IDS from  losing state first
# 				# get IDs being taken away
# 				#first check if any subtractions happen
# 				if all(i >=0 for i in item2) and not all(i == 0 for i in item2):
# 					#if not, generate new ids to add to state where things get added
# 					state_idx_add = np.where(item2 > 0)[0]
# 					for i in range(int(item2[state_idx_add])) :
# 						# use absolute value to capture incrementing negative IDs
# 						lastID = abs(lastID)+ 1
# 						if state_idx_add in [model.states_map[x] for x in patch2states]:
# 							lastID = -lastID
# 						if trackActors and eventActors:

# 							#add pair of actors to temp dict
# 							#get random actor from actor class by
# 							#choosing random ID from corresponding temp_stateDict
# 							increment_actors_dict(model, temp_actorPairsList ,idx2, lastID,temp_stateDict)

# 				    	temp_stateDict[state_idx_add].append(lastID)
# 				elif all(i <=0 for i in item2) and not all(i == 0 for i in item2):
# 					# next, check if there are any events that are just removals
# 					state_idx_remove = np.where(item2 < 0)[0]
# 					num_items_to_move = item2[state_idx_remove]
# 					ids_to_move = []
# 					for i in np.random.choice(temp_stateDict[state_idx_remove],np.abs(num_items_to_move),replace=False) :
# 					    ids_to_move.append(i)
# 					    if trackActors and eventActors:

# 						#add pair of actors to temp dict
# 						#get random actor from actor class by
# 						#choosing random ID from corresponding temp_stateDict
# 							increment_actors_dict(model, temp_actorPairsList ,idx2, i, temp_stateDict)
# 							# print temp_actorPairsList

# 					    temp_stateDict[state_idx_remove].remove(i)
# 				elif not all(i == 0 for i in item2):
# 					#lastly, go through events where IDs move from one state to another
# 					state_idx_remove = np.where(item2 < 0)[0]
# 					num_items_to_move = item2[state_idx_remove]
# 					ids_to_move = []
# 					for i in np.random.choice(temp_stateDict[state_idx_remove],np.abs(num_items_to_move),replace=False) :
# 					    ids_to_move.append(i)
# 					    if trackActors and eventActors:

# 						#add pair of actors to temp dict
# 						#get random actor from actor class by
# 						#choosing random ID from corresponding temp_stateDict
# 							increment_actors_dict(model, temp_actorPairsList ,idx2, i, temp_stateDict)
# 							# print temp_actorPairsList

# 					    temp_stateDict[state_idx_remove].remove(i)
# 					#add IDs to state that gets incremented
# 					state_idx_add = np.where(item2 > 0)[0]
# 					for i in ids_to_move :
# 						temp_stateDict[state_idx_add].append(i)





# 			for idx3, item in enumerate(model.states) :
# 				statesDict[item].append(temp_stateDict[idx3])

# 			if trackActors:
# 				for item in model.events:
# 					actorPairsDict[item[0]].append(temp_actorPairsList[item[0]])


# 	else :
# 		for idx, val in enumerate(t[:-1]) :
# 			# print "time index is", idx
# 			numIDs_to_move = np.zeros((model.N_events, model.N_states))
# 			for idx2, val2 in enumerate(tracking_array[:,idx]) :
# 				#calculate how many transitions to do

# 				numIDs_to_move[idx2,:] = model.transition[:,idx2]*val2

# 			temp_stateDict = [ list(statesDict[x][-1]) for x in model.states]
# 			for idx2,item2 in enumerate(numIDs_to_move) :
# 				for idx3, item3 in enumerate(item2):
# 				     if item3 < 0 :

# 				         #remove
# 				         for i in np.random.choice(temp_stateDict[idx3],np.abs(item3),replace=False) :
# 				             # print "removed id is", i
# 				             temp_stateDict[idx3].remove(i)
# 				     elif item3 > 0 :
# 				         for i in range(int(item3)) :
# 				         	#use absolute value to capture negative IDs
# 				               lastID = abs(lastID) +1
# 				               if idx3 in [model.states_map[x] for x in patch2states]:
# 				               		lastID = -lastID
# 				               temp_stateDict[idx3].append(lastID)
# 				               if trackActors and eventActors:
# 									increment_actors_dict(model, temp_actorPairsList ,idx2, i, temp_stateDict)


# 			for idx, item in enumerate(model.states) :
# 				statesDict[item].append(temp_stateDict[idx])
# 				#go through temp dictionary of actor pairs and append the ones for this time step
# 			if trackActors and eventActors:
# 				for item in model.events:
# 					actorPairsDict[item[0]].append(temp_actorPairsList[item[0]])


#     #Sort IDs in statesDict
# 	for x in model.states:
# 		for y in statesDict[x]:
# 			y.sort(key = abs)

# 	if trackActors:
# 		for x in model.events:
# 			for y in actorPairsDict[x[0]]:
# 				y.sort(key = lambda tup: (abs(tup[0]),abs(tup[1])))
# 		return statesDict, actorPairsDict
# 	else :
# 		return statesDict
