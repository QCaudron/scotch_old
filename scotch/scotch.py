# Helper functions
import json
import os
import numpy as np

"""
try :
	import pyximport
	pyximport.install(setup_args={"include_dirs":np.get_include()})
	import simulate_cython as simulate
	print "Imported Cython version"
except ImportError :
	import simulate
"""
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
			self.optional = { "default_algorithm" : "gillespie" } # Optional fields, like dataset, save name, ...
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

			# It's optional, but if it isn't defined, set the default algo
			if "default_algorithm" not in self.optional :
				self.optional["default_algorithm"] = "gillespie"
			
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

		out = ("scotch model with %d states, %d parameters, and %d events.\n" % (self.N_states, len(self.parameters), self.N_events))
		out += "\nStates :\n"

		for s in self.states :
			out += ("%s, initial condition = %d\n" % (s, self.initconds[s]))

		out += "\nParameters :\n"

		for p, v in self.parameters.items() :
			out += ("%s = %s\n" % (p, v))

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
			self.rates.append(eval("lambda X, time : %s" % helpers.parse(e[0], self.states_map, self.parameters)))
		
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







	def plot(self, T, **kwargs) :

		import matplotlib.pyplot as plt
		try :
			import seaborn
		except :
			pass

		t, trace = self.simulate(T, **kwargs)
		plt.plot(t, trace, lw=3)
		plt.legend(self.states)
		plt.xlabel("Time")
		plt.tight_layout()
		plt.show()







	def simulate(self, T, silent=False, **kwargs) :

		# Additional arguments for different algorithms
		algoparams = {
			simulate.tauLeap : ["tau"]
		}


		# Parameters to pass
		parameters = {}


		# Determine algorithm
		algorithm = eval("simulate." + kwargs.get("algorithm", self.optional["default_algorithm"]))

		
		# If not Gillespie, check that required parameters are present
		for algo, params in algoparams.items() :
			if algorithm == algo :
				for p in params :
					assert p in kwargs, "The parameter %s is required for the %s algorithm." % (p, algo)
					parameters[p] = kwargs[p]


		# Silent or no ?
		parameters["silent"] = silent


		# Run the algorithm
		if len(parameters) :
			return algorithm(self, T, **parameters)
		else :
			return algorithm(self, T)











	def sample(self, T, trajectories=100, bootstraps=1000, tvals=1000, alpha=0.05, **kwargs) :

		from scipy.interpolate import interp1d

		# Sample repeatedly from the model and potentially return summary statistics only
		all_t = []
		all_trace = []

		for traj in range(trajectories) :
			
			# Simulate the model
			t, trace = self.simulate(T, silent=True, **kwargs)

			# Append the time and traces to our arrays
			all_t.append(t)
			all_trace.append(trace)	


		# For each state variable, interpolate
		int_t = np.linspace(0, T, tvals)
		int_trace = {}

		for dim_num, dim in enumerate(self.states) :
			int_trace[dim] = []

			for x, y in zip(all_t, all_trace) :
				t = np.append(x, T)
				trace = np.append(y[:, dim_num], np.nan)
				int_trace[dim].append(interp1d(t, trace)(int_t))

			int_trace[dim] = np.array(int_trace[dim])


		# Calculate the mean
		m = { dim : np.nanmean(int_trace[dim], axis=0) for dim in self.states }



		# Bootstrap some 95% confidence intervals :
		means = {}

		# Draw a number of realisations with replacement
		idx = np.random.randint(0, trajectories, (bootstraps, trajectories))

		# For each dimension in the state space
		for dim in self.states :
			means[dim] = []
			
			# and for each bootstrap iteration
			for i in idx :
				# Calculate the means of this iteration
				means[dim].append(np.nanmean(int_trace[dim][i], axis=0))

			# After doing all iterations, sort the means
			means[dim] = np.sort(np.array(means[dim]), axis=0)

		# Extract intervals
		ci_low = { dim : means[dim][int(alpha*bootstraps/2.)] for dim in self.states }
		ci_high = { dim : means[dim][int(1.-alpha*bootstraps/2.)] for dim in self.states }

		return int_t, m, ci_low, ci_high










	def plotsamples(self, T, trajectories=100, bootstraps=1000, tvals=1000, alpha=0.05, **kwargs) :

		import matplotlib as mpl
		import matplotlib.pyplot as plt
		C = mpl.rcParams["axes.color_cycle"]

		try :
			import seaborn as sns
			C = sns.color_palette("deep", 6)
		except ImportError :
			pass

		t, mean, dn, up = self.sample(T, trajectories, bootstraps, tvals, alpha, **kwargs)
		for s, state in enumerate(self.states) :
			plt.plot(t, mean[state], lw=3)
			plt.fill_between(t, dn[state], up[state], alpha=0.4, color=C[s % 6])
		plt.legend(self.states)
		plt.xlabel("Time")
		plt.tight_layout()
		plt.show()






