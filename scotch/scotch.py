# Helper functions
import json
import os
import numpy as np
from scipy.interpolate import interp1d

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
	"""
	scotch model object

	The model is scotch's basic object class, allowing
	access to all of the features in scotch.

	The following functions all have docstrings, call
	?scotch.model.<function>
	for more information on these methods.


	model()
	Model Creation
	--------------

	model = scotch.model()
	model = scotch.model("scotch_model_file.json")

	Create a model from scratch, or load a previous model.


	wizard()
	Creation using the Wizard
	-------------------------

	model.wizard()

	Invoke the wizard to guide you through model creation.


	save()
	Save a model to file
	--------------------

	model.save()

	Save a complete scotch model to JSON file for later use.


	plot()
	Plot one realisation of the stochastic model
	--------------------------------------------

	model.plot()

	Draw a realisation of the stochastic process up to some time,
	and plot the full state space.


	simulate()
	Return the trace of a realisation
	---------------------------------

	model.simulate()

	Draw a realisation of the stochastic process up to some time,
	and return the state space as a function of time.


	sample()
	Return summary statistics
	-------------------------

	model.sample()

	Sample multiple realisations of the stochastic process, and
	return the mean and confidence intervals of the realisations.


	plotsamples()
	Plot the mean and CIs of multiple realisations
	----------------------------------------------

	model.plotsamples()

	Sample multiple realisations of the stochastic process, and
	plot the means and confidence intervals of each state in the
	system.

	"""




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
		"""
		scotch.model.save(filename=None)
		--------------------------------

		Save a complete scotch model to JSON file for later use.
		
		Filename can be a string defining a local or complete path,
		including filename in which to save the model.

		If Filename is None, the model is saved to the location 
		specified in the model.optional dictionary. If this is empty, 
		Filename is defined as "./scotch_model.json".

		"""

		# If no filename is provided, grab the last one used,
		# or provide one if we've never saved this model
		if filename is None :
			filename = self.optional.get("Filename", "scotch_model.json")

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
		"""
		scotch.model.wizard()
		--------------------------------

		Invoke the wizard to guide you through model creation.

		This is an interactive function that will ask you the names
		of your system's states, their initial conditions, the 
		parameters in the system and their values, and the expressions
		that define the rate at which transitions occur between states.

		"""

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
		"""
		scotch.model.plot(T, **kwargs)
		------------------------------

		Plot one realisation of the stochastic model.

		T is the time until which the system is simulated.

		A number of optional arguments can be passed to this function.

		algorithm="gillespie", algorithm="tauLeap"
		Use the exact Gillespie Stochastic Simulation Algorithm, or
		a tau-leaping approximation for speed. More algorithms to come.

		If algorithm="tauLeap", you may want to specify
		tau=delta_t, where delta_t is the timestep at which tau-leaping
		should be done. 
		By default, tau=1.

		If no algorithm is passed, we use the default algorithm as
		defined in the model. If none is set, it defaults to Gillespie.

		silent=False, silent=True
		If silent, don't use progress bars or return warnings.
		By default, silent=False.

		propagate=False, propagate=True
		If propagate, don't rebuild the model to initial conditions
		every time this is run; carry forward the last state space.
		By default, propagate=False.

		"""

		# Try to plot things beautifully
		import matplotlib.pyplot as plt
		try :
			import seaborn
		except :
			pass

		# If the user specifies they want to track, we cancel that;
		# this method returns nothing
		kwargs.pop("track", None)

		# Simulate
		t, trace = self.simulate(T, **kwargs)

		# Plot everything
		plt.plot(t, trace, lw=3)
		plt.legend(self.states)
		plt.xlabel("Time")
		plt.xlim(0, t[-1])
		plt.tight_layout()
		plt.show()








	def simulate(self, T, **kwargs) :
		"""
		t, trace, [track] = scotch.model.simulate(T, **kwargs)
		------------------------------------------------------

		Return the trace of a realisation.

		T is the time until which the system is simulated.

		A number of optional arguments can be passed to this function.

		algorithm="gillespie", algorithm="tauLeap"
		Use the exact Gillespie Stochastic Simulation Algorithm, or
		a tau-leaping approximation for speed. More algorithms to come.

		If algorithm="tauLeap", you may want to specify
		tau=delta_t, where delta_t is the timestep at which tau-leaping
		should be done. 
		By default, tau=1.

		If no algorithm is passed, we use the default algorithm as
		defined in the model. If none is set, it defaults to Gillespie.

		silent=False, silent=True
		If silent, don't use progress bars or return warnings.
		By default, silent=False.

		propagate=False, propagate=True
		If propagate, don't rebuild the model to initial conditions
		every time this is run; carry forward the last state space.
		By default, propagate=False.

		track=False, track=True, 
		If track, we track all transitions as they occur and return
		these as a third output variable.
		By default, track=False. Tracking slows simulations considerably.

		"""


		# Determine algorithm
		algorithm = eval("simulate." + kwargs.get("algorithm", self.optional["default_algorithm"]))

		# Run the algorithm
		return algorithm(self, T, **kwargs)
		









	def sample(self, T, trajectories=100, bootstraps=500, tvals=1000, alpha=0.95, silent=False, **kwargs) :
		"""
		t, means, CI_low, CI_high = scotch.model.sample(T, trajectories=100, bootstraps=500, tvals=1000, alpha=0.95)
		------------------------------------------------------------------------------------------------------------

		Return summary statistics.

		T is the time until which the system is simulated.

		trajectories is the number of realisations to simulate.

		bootstraps is the number of bootstrap samples to draw to 
		compute the confidence intervals.
		bootstraps=0 means CI_low and CI_high are not returned;
		only the mean trajectory is calculated.

		tvals is the number of time values to interpolate over to compute
		means and confidence intervals, and the number of time values
		returned to the user.

		alpha is the level at which confidence intervals are computed.
		The default, alpha=0.95, returns 95% confidence intervals around
		the mean of the trajectories.

		A number of optional arguments can be passed to this function.

		algorithm="gillespie", algorithm="tauLeap"
		Use the exact Gillespie Stochastic Simulation Algorithm, or
		a tau-leaping approximation for speed. More algorithms to come.

		If algorithm="tauLeap", you may want to specify
		tau=delta_t, where delta_t is the timestep at which tau-leaping
		should be done. 
		By default, tau=1.

		If no algorithm is passed, we use the default algorithm as
		defined in the model. If none is set, it defaults to Gillespie.

		silent=False, silent=True
		If silent, don't use progress bars or return warnings.
		By default, silent=False.

		propagate=False, propagate=True
		If propagate, don't rebuild the model to initial conditions
		every time this is run; carry forward the last state space.
		By default, propagate=False.

		track=False, track=True, 
		If track, we track all transitions as they occur and return
		these as a third output variable.
		By default, track=False. Tracking slows simulations considerably.

		"""

		# Sample repeatedly from the model and return summary statistics only
		all_t = []
		all_trace = []

		if not silent :
			print "Sampling trajectories."
			helpers.progBarStart()

		# For each trajectory index :
		for traj in range(trajectories) :

			if not silent :
				helpers.progBarUpdate([traj-1, traj], trajectories)
			
			# Simulate the model
			t, trace = self.simulate(T, silent=True, **kwargs)

			# Append the time and traces to our arrays
			all_t.append(t)
			all_trace.append(trace)	


		if not silent :
			print "\n"


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



		if bootstraps :
			# Bootstrap some 95% confidence intervals :
			means = {}

			# Draw a number of realisations with replacement
			idx = np.random.randint(0, trajectories, (bootstraps, trajectories))


			if not silent :
				print "Bootstrapping."
				helpers.progBarStart()


			# For each dimension in the state space
			for dimidx, dim in enumerate(self.states) :
				means[dim] = []

				
				# and for each bootstrap iteration
				for iidx, i in enumerate(idx) :
					# Calculate the means of this iteration
					means[dim].append(np.nanmean(int_trace[dim][i], axis=0))

					if not silent :
						helpers.progBarUpdate([dimidx*(iidx-1), dimidx*iidx], len(self.states)*bootstraps)

				# After doing all iterations, sort the means
				means[dim] = np.sort(np.array(means[dim]), axis=0)


			# Extract intervals
			ci_low = { dim : means[dim][int((1-alpha)*bootstraps/2.)] for dim in self.states }
			ci_high = { dim : means[dim][int(1.-(1-alpha)*bootstraps/2.)] for dim in self.states }

			# Return everything
			return int_t, m, ci_low, ci_high

		else :
			return int_t, m











	def plotsamples(self, T, trajectories=100, bootstraps=1000, tvals=1000, alpha=0.95, silent=False, **kwargs) :
		"""
		scotch.model.plotsamples(T, trajectories=100, bootstraps=500, tvals=1000, alpha=0.95)
		-----------------------------------------==------------------------------------------

		Plot the mean and CIs of multiple realisations.

		T is the time until which the system is simulated.

		trajectories is the number of realisations to simulate.

		bootstraps is the number of bootstrap samples to draw to 
		compute the confidence intervals.
		bootstraps=0 means CI_low and CI_high are not returned;
		only the mean trajectory is calculated.

		tvals is the number of time values to interpolate over to compute
		means and confidence intervals, and the number of time values
		returned to the user.

		alpha is the level at which confidence intervals are computed.
		The default, alpha=0.95, returns 95% confidence intervals around
		the mean of the trajectories.

		A number of optional arguments can be passed to this function.

		plot=["State1", "State2"]
		If not specified, plot all of the states in the model. Otherwise,
		plot only those listed; the names must be those used in the model.

		algorithm="gillespie", algorithm="tauLeap"
		Use the exact Gillespie Stochastic Simulation Algorithm, or
		a tau-leaping approximation for speed. More algorithms to come.

		If algorithm="tauLeap", you may want to specify
		tau=delta_t, where delta_t is the timestep at which tau-leaping
		should be done. 
		By default, tau=1.

		If no algorithm is passed, we use the default algorithm as
		defined in the model. If none is set, it defaults to Gillespie.

		silent=False, silent=True
		If silent, don't use progress bars or return warnings.
		By default, silent=False.

		propagate=False, propagate=True
		If propagate, don't rebuild the model to initial conditions
		every time this is run; carry forward the last state space.
		By default, propagate=False.

		track=False, track=True, 
		If track, we track all transitions as they occur and return
		these as a third output variable.
		By default, track=False. Tracking slows simulations considerably.

		"""

		import matplotlib.pyplot as plt

		# Define a nice colour palette
		try :
			import seaborn as sns
			C = sns.color_palette("deep", 6)
		except ImportError :
			import matplotlib as mpl
			C = mpl.rcParams["axes.color_cycle"]

		# Sample everything
		t, mean, dn, up = self.sample(T, 
									  trajectories=trajectories, 
									  bootstraps=bootstraps, 
									  tvals=tvals, 
									  alpha=alpha, 
									  silent=silent, 
									  **kwargs)

		# Determine which states we want to plot
		statestoplot = kwargs["plot"] if "plot" in kwargs else self.states

		# Plot them
		for s, state in enumerate(statestoplot) :
			plt.plot(t, mean[state], lw=3)
			plt.fill_between(t, dn[state], up[state], alpha=0.4, color=C[s % 6])

		# Make pretty
		plt.legend(statestoplot)
		plt.xlabel("Time")
		plt.xlim(0, T)
		plt.tight_layout()
		plt.show()








	# Do we still need this ?
	"""
	def trackindividuals(self, t=None, tracked=None, sampleto=0, **kwargs) :

		if sampleto :
			t, trace, tracked = self.simulate(sampleto, track=True, **kwargs)

		return helpers.trackIndividuals(self, tracked, t, **kwargs)
	"""



# PROBLEMS :
# 
# Tauleap state space still goes negative occasionally; seems dependent on tau / tmax
# Round up still required in defining trace[] array in tauleap ? Added; check it works
# Progbar for bootstrapping in sample() and plotsamples() is epic fail
# Require constraints on events : don't do X if Y == 0, for example
# Found a ripple in the spacetime continuum
