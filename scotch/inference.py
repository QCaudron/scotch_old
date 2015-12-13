import numpy as np
import helpers




def MLE(model, t, trace, eventseq, combinations=None) :

    # Calculate the maximum likelihood estimate for all parameters,
    # using the exact SSA algorithm to obtain completely-observed traces.

    # Estimates go here
    estimates = np.zeros(len(model.parameters))

    # Array of event indices
    # It we're given an indicator array of 0 and 1 with a column for each event,
    # collapse it down to the index of the event that took place at that time
    if len(eventseq.shape) > 1 :
        if eventseq.shape[1] > 1 :
            eventseq = [np.where(eventseq[i, :] == 1)[0][0] \
                for i in range(len(eventseq))]

    # The number of times each event took place in the realisation
    numberEvents = [eventseq.count(i) for i in range(len(model.events))]

    # How many ways could these events occur, as a function of state space ?
    # If we aren't passed this, try to calculate it.
    # Example : for the infection term in SIR models, beta*S*I, there are
    # S*I ways that an infection could take place, so calculate that,
    # as a function of the state space every time an event occurs
    if not combinations :
        combinations = []
        for X in trace[:-1] :
            combinations.append([eval(
                helpers.parse(model.events[i][0],
                              model.states_map,
                              model.parameters,
                              onlyStates=True)) for i in range(len(model.events))])
        combinations = np.array(combinations)

    # If we're passed something, it's in the form of an array with one
    # entry per event, containing a string in the form "S*I" where S, I are states.
    # Parse this and ...

    # Estimate the overall rate constant for each reaction
    for param in range(len(model.parameters)) :
        estimates[param] += numberEvents[param] / np.sum(combinations[:, param] * np.diff(t))


    return estimates
