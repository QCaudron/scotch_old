# Helper functions
import json
import os
import numpy as np

import helpers
import simulate






# Model class

class model(object) :

	# Descriptors
	def __name__(self) :
		return "scotch Markov process model."


	# Constructor
	def __init__(self, filename=None) :
		"""Construct a scotch model object."""



		# Default, blank constructor
		if filename is None :

			self.states = [] # State variables
			self.initconds = {} # Initial conditions
			self.parameters = {} # Parameters
			self.reactions = [] # Reactions
			self.optional = {} # Optional fields, like dataset, save name, ...
			self.states_map = {} # Map between state symbols and vector notation
			self.transition = None # Transition matrix
			self.tracked_states = None #State variables to be tracked during simulation
			self.tracked_trans = None #Transitions to be tracked during simulation





		# Construct from existing file
		else :

			# Read the data from the file
			with open(filename, "r") as f :
				model = json.load(f)

			# Ensure that the min required fields are present and not empty
			not_present = [req for req in helpers.required if req not in model]
			if not_present :
				raise helpers.InvalidModel("%s not found in the scotch model %s." %
					(", ".join(not_present), f))


			# Read in available data
			self.states = model["States"]
			self.initconds = model["InitialConditions"]
			self.parameters = model["Parameters"]
			self.reactions = model["Reactions"]

			# Read in optional data
			missing = list(set(model).difference(helpers.required)) # additional fields
			self.optional = { i : model[i] for i in missing }
			
			# Some model stuff
			self.build()









	# Short representation of model objects
	def __repr__(self) :

		out = ""

		for r in self.reactions :
			out += ("%s -> %s, rate %s\n" % (r[0], r[1], r[2]))

		return out






	# Long representation of model objects
	def __str__(self) :

		out = ("scotch.scotch.model with %d states, %d parameters, and %d reactions.\n" % (self.N_states, len(self.parameters), self.N_reactions))
		out += "\nStates :\n"

		for s in self.states :
			out += ("%s, initial condition = %d\n" % (s, self.initconds[s]))

		out += "\nParameters :\n"

		for p, v in self.parameters.items() :
			out += ("%s = %s\n" % (p, v))

		out += "\nReactions :\n"
		count = 0
		for r in self.reactions :
			out += ("Number %s: %s -> %s,\trate %s\n" % (count,r[0], r[1], r[2]))
			count +=1

		return out









	# Save model
	def save(self, filename=None) :
		"""Save the model to a JSON file."""

		# If no filename is provided, grab the last one used,
		# or provide one if we've never saved this model
		if filename is None :
			filename = self.optional["Filename"] if "Filename" in self.optional else "scotch_model.json"

		# Save filename for next time
		self.optional["Filename"] = filename

		# Generate dictionary for writing to JSON with required fields
		out = { "States" : self.states,
				"InitialConditions" : self.initconds,
				"Parameters" : self.parameters,
				"Reactions" : self.reactions }
		
		# Add optional fields if any exist
		for optional_field, optional_value in self.optional.items() :
			out[optional_field] = optional_value

		# Write to JSON
		with open(filename, "w") as f :
			json.dump(out, f, sort_keys=True, indent=4, separators=(",", " : "))











	# If data is entered manually, then fill in the blanks
	def build(self, silent=False) :
		"""Build the model if it is entered manually."""

		# Model variables
		self.N_states = len(self.states)
		self.N_reactions = len(self.reactions)
		self.states_map = { i : idx for i, idx in zip(self.states, range(self.N_states)) }

		# Transition matrix
		self.transition = np.zeros((self.N_states, self.N_reactions), dtype=int)
		for i, val in enumerate(self.reactions) :
			if val[0] in self.states :
				self.transition[self.states_map[val[0]], i] = -1
			if val[1] in self.states :
				self.transition[self.states_map[val[1]], i] = 1

		# State vector
		self.X = np.zeros(self.N_states)
		for key, val in self.initconds.items() :
			self.X[self.states_map[key]] = val

		# Transition rate functions
		self.rates = []
		for i, val in enumerate(self.reactions) :
			self.rates.append(eval("lambda X : %s" % helpers.parse(val[2], self.states_map, self.parameters)))

		# Rewrite states as not unicode
		for idx,s in enumerate(self.states) :
			self.states[idx] = s.encode("utf-8")

		# Rewrite reactions as not unicode
		for idx1, r in enumerate(self.reactions) :
			for idx2,r2 in enumerate(r) :
				self.reactions[idx1][idx2] = r[idx2].encode("utf-8")


		# print "Would you like to track any reactions? (y/n)"
		# reaction_tracker_ind = raw_input()

		# if reaction_tracker_ind == "y" :
		# 	print self
		# 	print "Which reactions would you like to track? (enter Reaction Numbers separated by commas)"
		# 	num_tracked_trans = raw_input().split(",")
		# 	print num_tracked_trans
		# 	self.tracked_trans = [self.reactions[int(x)] for x in num_tracked_trans] 
		# 	#self.tracked_trans = self.reactions[ [int(x) for x in num_tracked_trans] ]
		# 	print self.tracked_trans
		# 	#generate tracked states from transitions
		# 	self.tracked_states = []
		# 	for t in self.tracked_trans :
		# 		for t2 in t :
		# 			if (t2 in self.states and t2 not in self.tracked_states):
		# 				self.tracked_states.append(t2)


		# 	#	for y in x :
		# 	# 		if y not in self.states :
		# 	# 		 	print("Error:", y ," is not a valid state")
		# 	# 		 	self.tracked_trans = None
		# 	# 		 	self.tracked_states = None
		# 	# 		else :
		# 	# 		 	if y not in self.tracked_states :
		# 	# 		 		self.tracked_states.append(y)





		# 	#build in check to make sure states are real states
		# 	#for t in self.tracked_trans :


		# else :
		# 	print "Would you like to track any states? (y/n)"
		# 	state_tracker_ind = raw_input()

		# 	if state_tracker_ind == "y":
		# 		print "Which states would you like to track? (Enter states separated by commas)"
		# 		print self.states
		# 		self.tracked_states = raw_input().replace(" ", "").split(",")

		
		if not silent :
			print self










	def wizard(self) :
		"""Interactively generate a model."""

		# Variables
		print "Complete list of state variables, separated by commas :"
		self.states = raw_input().replace(" ", "").split(",")
		self.N_states = len(self.states)
		self.states_map = { s : idx for s, idx in zip(self.states, range(self.N_states)) }

		# Initial condition for each variable
		print "\nInitial conditions (integers) :"
		self.initconds = { s : int(raw_input("%s : " % s)) for s in self.states }
		
		# Parameters
		print "\nComplete list of parameters, separated by commas :"
		params = raw_input().replace(" ", "").split(",")

		# Value of each parameter
		print "\nValues of parameters :"
		self.parameters = { p : raw_input("%s : " % p) for p in params }

		# State transitions
		reaction = []
		self.reactions = []
		print "\nReactions, as <from>, <to>, <rate> triplets :"
		while True :
			reaction = raw_input().split(",")
			if len(reaction) != 3 :
				break
			self.reactions.append(tuple([reaction[0].strip(), 
										 reaction[1].strip(), 
										 reaction[2].strip()]))

		# Model variables
		self.build()







	def plot(self, T, algorithm=simulate.gillespie) :

		import matplotlib.pyplot as plt
		try :
			import seaborn
		except :
			pass

		t, trace = simulate.gillespie(self, T)
		plt.plot(t, trace)
		plt.legend(self.states)
		plt.show()



# CURRENTLY : -----------------------
# line 20 simulate.py
# TypeError: float() argument must be a string or a number
# Check parsing of parameters






