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
			self.events = [] # Events
			self.optional = { "default_algorithm" : "simulate.gillespie" } # Optional fields, like dataset, save name, ...
			self.states_map = {} # Map between state symbols and vector notation
			self.transition = None # Transition matrix
			# self.tracked_states = None #State variables to be tracked during simulation
			# self.tracked_trans = None #Transitions to be tracked during simulation






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
			self.events = model["Events"]

			# Read in optional data
			missing = list(set(model).difference(helpers.required)) # additional fields
			self.optional = { i : model[i] for i in missing }
			
			# Some model stuff
			self.build()









	# Short representation of model objects
	def __repr__(self) :

		out = ""

		for e in self.events :
			out += ("rate %s\n" % (e[0]))

		return out






	# Long representation of model objects
	def __str__(self) :

		out = ("scotch.scotch.model with %d states, %d parameters, and %d events.\n" % (self.N_states, len(self.parameters), self.N_events))
		out += "\nStates :\n"

		for s in self.states :
			out += ("%s, initial condition = %d\n" % (s, self.initconds[s]))

		out += "\nParameters :\n"

		for p, v in self.parameters.items() :
			out += ("%s = %s\n" % (p, v))

		out += "\nEvents :\n"
		count = 0
		for e in self.events :
			out += ("Number %s: \tprobability %s\n" % (count,e[0]))
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
				"Events" : self.events }
		
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
		self.N_events = len(self.events)
		self.states_map = { i : idx for i, idx in zip(self.states, range(self.N_states)) }

		# Transition matrix
		self.transition = np.zeros((self.N_states, self.N_events), dtype=int)
		for idx, e in enumerate(self.events) :
			for i in e[1] :
				self.transition[self.states_map[i], idx] = e[1][i]


		# State vector
		self.X = np.zeros(self.N_states)
		for key, val in self.initconds.items() :
			self.X[self.states_map[key]] = val

		# Transition rate functions
		self.rates = []
		for e in self.events :
			self.rates.append(eval("lambda X : %s" % helpers.parse(e[0], self.states_map, self.parameters)))

		# # Rewrite states as not unicode
		# for idx,s in enumerate(self.states) :
		# 	self.states[idx] = s.encode("utf-8")

		# # Rewrite reactions as not unicode
		# for idx1, r in enumerate(self.events) :
		# 	self.events[idx1][0]=r[0].encode("utf-8")
		# 	for item in r[1].keys() :
		# 		self.events[1][idx2] = r[idx2].encode("utf-8")


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
		event = []
		self.events = []
		print "\nEvents, as \"<rate>, <state_change>, ...\" lists, with commas between state changes and X+1, Y-1 as example changes :"
		while True :
			
			# Grab user input of one event
			event = raw_input().split(",")
			if event == [""] : # if they hit Enter
				break # stop reading in events

			thisevent = {}
			for e in event[1:] :
				if "+" in e :
					st, quant = e.split("+")
					quant = int(quant)
				elif "-" in e :
					st, quant = e.split("-")
					quant = -int(quant)
				else :
					raise helpers.InvalidModel("The syntax of this event was not recognised.")
				thisevent[st.strip()] = quant

			self.events.append([event[0].strip(), thisevent])

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







	def simulate(self, T, **kwargs) :

		# Additional arguments for different algorithms
		algoparams = {
			simulate.tauLeap : ["tau"]
		}


		# Determine algorithm
		algorithm = kwargs.get("algorithm", eval("simulate." + self.optional["default_algorithm"]))

		
		# If not Gillespie, check that required parameters are present
		for algo, params in algoparams.items() :
			if algorithm == algo :
				for p in params :
					assert p in kwargs, "The parameter %s is required for the %s algorithm." % (p, algo)


		# Are we tracking individuals ?
		tracking = kwargs.get("track", False)
		if tracking :
			incremental = kwargs.get("incremental", False)













