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




def trackIndividuals(model, tracking_array, t) :
	# Initialize dictionary of arrays by state
	statesDict = {}
	for s in model.states :
		statesDict[s] = []

	

	# Input initial conditions
	lastID = 0

	for key in statesDict.keys() :
		if model.initconds[key] >0 :
			statesDict[key].append(range(lastID, lastID+model.initconds[key]))
			lastID = lastID+model.initconds[key]
		else :
			statesDict[key].append([])

	
	
	for idx, val in enumerate(t[:-1]) :
		for idx2, val2 in enumerate(tracking_array[:,idx]) :
			#calculate how many transitions to do 
			numIDs_to_move = model.transition[:,idx2]*val2
			for idx3, val3 in enumerate(numIDs_to_move) :
				x = statesDict[model.states[idx3]][-1]
				if val3 < 0 :
					#remove
					for i in np.random.choice(x,np.abs(val3),replace=False) :
						x.remove(i)
				elif val3 > 0 :
					for i in range(int(val3)) :
						lastID+=1
						x.append(lastID)
				statesDict[model.states[idx3]].append(x)

						
	return statesDict




# def trackIndividuals(model, individuals, transition, t, incremental=False) :

# 	pass



