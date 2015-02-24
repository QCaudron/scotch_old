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










# Parse user-input 

def parse(S, states_map=[], params=[]) :

	# Buffer ( substrings between operators ), and parsed list
	buff = []
	out = []
    
    # Operators
	symbols = ["+", "-", "*", "/", "(", ")", "#"]

	S = S.replace(" ", "") + "#"
    
	# For each character in the string to be parsed
	for s in S :
        
        # If it's an operator
		if s in symbols :
            
            # Generate a string from what's currently in the buffer
			buff = "".join(buff)
            
            # If it's a parameter, wrap it in ()
			if buff in params :
				out.append("(%s)" % parse(params[buff]))
                
            # Else, if it's a state variable, replace it with vector notation
			elif buff in states_map :
				out.append("int(X[%d])" % states_map[buff])
                
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
    
    # Return a string that should fit in eval()
	return "".join(out)










def progBarStart(width=25) :

	sys.stdout.write("[%s]" % (" " * width))
	sys.stdout.flush()
	sys.stdout.write("\b" * (width+1))




def progBarUpdate(t, tmax, width=25) :
	
	if np.fmod(t[0] / float(tmax), 1./width) > np.fmod(t[-1] / float(tmax), 1./width) :
		sys.stdout.write("-")
		sys.stdout.flush()




def trackIndividuals(model, tracking_array, t, keepIndividuals = True) :
	# Initialize dictionary of arrays by state
	statesDict = {}
	for s in model.states :
		statesDict[s] = []

	

	# Input initial conditions
	lastID = 0

	for key in statesDict.keys() :
		if model.initconds[key] >0 :
			statesDict[key].append(range(lastID, lastID+model.initconds[key]))
			lastID += model.initconds[key]
		else :
			statesDict[key].append([])


	# Check if user wants to keep ids between states or not
	# do something about source and sink states
	if keepIndividuals:
		#Go through each time step
		for idx, val in enumerate(t[:-1]) :
			# reset matrix of number of IDs to move (number of events by number of states)
			numIDs_to_move = np.zeros((model.N_events, model.N_states))
			for idx2, val2 in enumerate(tracking_array[:,idx]) :
				#calculate how many transitions to do          
				numIDs_to_move[idx2,:] = model.transition[:,idx2]*val2
			# set up temporary list of ids in the latest timestep for each state
			temp_stateDict = [ list(statesDict[x][-1]) for x in model.states] 
			# go through each event and move ids to/from appropriate states      
			for idx2,item2 in enumerate(numIDs_to_move) :
				# go through each state in order and remove or add items
				# need to always take IDS from  losing state first
				# get IDs being taken away
				#first check if any subtractions happen
				if all(i >=0 for i in item2) and not all(i == 0 for i in item2):
					#if not, generate new ids to add to state where things get added
					state_idx_add = np.where(item2 > 0)[0]
					for i in range(int(item2[state_idx_add])) :
						lastID +=1
				        temp_stateDict[state_idx_add].append(lastID)
				elif not all(i == 0 for i in item2):
					state_idx_remove = np.where(item2 < 0)[0]
					num_items_to_move = item2[state_idx_remove]
					ids_to_move = []
					for i in np.random.choice(temp_stateDict[state_idx_remove],np.abs(num_items_to_move),replace=False) :
					    ids_to_move.append(i)
					    temp_stateDict[state_idx_remove].remove(i)
					#add IDs to state that gets incremented    
					state_idx_add = np.where(item2 > 0)[0]
					for i in ids_to_move :
						temp_stateDict[state_idx_add].append(i)


			for idx3, item in enumerate(model.states) :
				statesDict[item].append(temp_stateDict[idx3])                                       

	else :
		for idx, val in enumerate(t[:-1]) :
			# print "time index is", idx 
			numIDs_to_move = np.zeros((model.N_events, model.N_states))
			for idx2, val2 in enumerate(tracking_array[:,idx]) :
				#calculate how many transitions to do 
				# print "This many", val2,"of this transition", model.transition[:,idx2]            
				numIDs_to_move[idx2,:] = model.transition[:,idx2]*val2
			# print "num IDs to move is", numIDs_to_move
			temp_stateDict = [ list(statesDict[x][-1]) for x in model.states]       
			for idx2,item2 in enumerate(numIDs_to_move) :
				for idx3, item3 in enumerate(item2):
				     if item3 < 0 :
				         # print "time index is", idx
				         # print "temp list is", temp_stateDict[idx3]
				         #print "trace is",trace[idx,:]
				         #remove
				         for i in np.random.choice(temp_stateDict[idx3],np.abs(item3),replace=False) :
				             # print "removed id is", i
				             temp_stateDict[idx3].remove(i)
				     elif item3 > 0 :
				         for i in range(int(item3)) :
				               lastID+=1
				               temp_stateDict[idx3].append(lastID)
				         #       print "appended temp list is", temp_stateDict[idx3]
				         # print "time index is", idx
				         # print "last added item is", lastID
	                                
	                     
			#print "new x for state", item, "is", x  
			for idx, item in enumerate(model.states) :
				statesDict[item].append(temp_stateDict[idx])                                       

						
	return statesDict




# def trackIndividuals(model, individuals, transition, t, incremental=False) :

# 	pass



