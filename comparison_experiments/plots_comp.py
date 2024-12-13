import pandas
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cm as cm
import numpy as np
import datetime
import os
import re
import sys
from pathlib import Path
from matplotlib import ticker as mticker

# GLOBAL VARIABLES
# FYI: currently markers and colors only allow for 10 algorithms in one plot, each with a distinctive marker and color
ALLOWED_ALGOS_WITH_LABEL =  {'rosko':'Rosko',
							 'rosko_base':'Rosko Baseline', 
                             'numpy_arr':'NumPy-Dense', 
                             'numpy_csr':'NumPy-CSR', 
                             'naive':'Naive', 
                             'numpy_dense':'NumPy-Dense, zeros stripped', 
                             'numpy_dia':'Numpy-Diagonal'}
ALLOWED_SPARSITY_PATTERNS = ['random-uniform', 
                             'row-pattern', 
                             'diagonal', 
                             'column-pattern'] # If changed, then update makeTitle()

DEBUG = False

#set env path to root directory ?? for python liibrary function to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plotslib.plot_utils import getPlotsDirectory, directoriesFromTime
	

def plot_comparison(algos, sparsities, sparsity_pattern, labels, title, results_fname, env_details, fname = "plot_comp"):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','k','r','r']
	# markers = ['o', 'v', 's', 'd', '^', 'p', '*', 'h', 'x', '+']
	# colors = ['b', 'g', 'k', 'r', 'c', 'm', 'y', 'orange', 'purple', 'brown']
	dft = pandas.read_csv(results_fname)
	# runs = dft['runs'].iloc[0]

	# create results folders if not there and put plots in them, and get time
	file_path = Path('./' + results_fname)
	creation_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
	plotsDir, dateStr = directoriesFromTime(creation_datetime, os.getcwd())
	
	plt.figure(figsize = (6,4))
	for i in range(len(algos)):
		algo_time = dft[dft['algo'] == algos[i]]['time'].values
		algo_sparsities = dft[dft['algo'] == algos[i]]['sp'].values
		if algos[i] == 'rosko_base':
			plt.plot(algo_sparsities, algo_time, ls = '--', label = labels[i], marker = markers[i], color = colors[i])
		else:	
			plt.plot(algo_sparsities, algo_time, label = labels[i], marker = markers[i], color = colors[i])
		
	
	# plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('(b) SDMM on Intel Core i7 using\n' + title, fontsize = 18 )
	# plt.title('(a) SDMM on Intel Core i5 using ' + title, fontsize = 18 )
	plt.xlabel("Sparsity [%]", fontsize = 16)
	plt.ylabel("Running time [sec]", fontsize = 16)
	plt.yticks( fontsize = 10)
	plt.xticks( fontsize = 10)
	# num_ticks = len(sparsities) # Number of x-ticks you want
	# plt.xticks(np.linspace(min(sparsities), max(sparsities), num_ticks), fontsize=10)
	# plt.xticks(np.asarray(sparsities, dtype=float), fontsize=10)
	plt.legend(loc = "upper right", prop={'size': 12})
	# plt.savefig("%s_perf.pdf" % (fname), bbox_inches='tight')
	# plt.savefig("%s%s_%s_r%s_perf.pdf" % (plotsDir, dateStr, fname, runs), bbox_inches='tight')
	plt.savefig("%s%s_%s_%s_%s_perf.pdf" % (plotsDir, dateStr, fname, sparsity_pattern, env_details), bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')


def isAlgoValid(algo):
	
	# Check if algo is a direct match in ALLOWED_ALGOS_WITH_LABEL
    if algo in ALLOWED_ALGOS_WITH_LABEL:
        return "all", True
    
    # If not directly valid, check for a split possibility
    if "_" in algo:
        first_half, second_half = algo.split("_", 1)  # Split at the first underscore only
        
        # Check if the first part is a valid key in ALLOWED_ALGOS_WITH_LABEL
        if first_half in ALLOWED_ALGOS_WITH_LABEL:
            return "first half",True
    
    # If neither condition is met, return False
    return "nothing", False

 
def makeTitle(sparsity_pattern):
    
	title = ""

	if sparsity_pattern=='random-uniform':
		title = "random uniform sparse matrices"
	elif sparsity_pattern=='row-pattern':
		title = "row-pattern sparse matrices"
	elif sparsity_pattern=='diagonal':
		title = "diagonal pattern sparse matrices"
	elif sparsity_pattern=='column-pattern':
		title = "column-pattern sparse matrices"
	else:
		# print(sparsity_pattern + " is not a valid type of sparsity pattern\n")
		raise ValueError(f"Sparsity pattern '{sparsity_pattern}' is not allowed.")
		sys.exit()

	return title


def makeLabel(matchType, algo):

	if matchType == "all":
		return ALLOWED_ALGOS_WITH_LABEL[algo]
	if matchType == "first half":
		first_half, second_half = algo.split("_", 1)  # Split on first underscore only
		return f"{ALLOWED_ALGOS_WITH_LABEL[first_half]}, with {second_half}" # Only for handling p=x
	else:
		raise ValueError(f"There is no valid label for algorithm {algo}.")


def main():
    
	if DEBUG: print(sys.argv)
 
    # Read the type of sparsity pattern from input
	sparsity_pattern = sys.argv[1]
	if sparsity_pattern not in ALLOWED_SPARSITY_PATTERNS:
		# print(sparsity_pattern + " is not a valid type of sparsity pattern\n")
		raise ValueError(f"Sparsity pattern '{sparsity_pattern}' is not allowed.")
		sys.exit()

	# Read the algorithms used in the experiment and write them in algos array
	num_algos = int(sys.argv[2])
	algos = []
	labels = []

	for i in range(num_algos):
		algo = sys.argv[3+i]
		matchType, isValid = isAlgoValid(algo)
		if isValid:
			algos.append(algo)
			label = makeLabel(matchType, algo)
			labels.append(label)
		else:
			raise ValueError(f"Algorithm '{algo}' is not allowed.")

	# Read the sparsity values used in experiment and write them in sparsities array
	num_sparsities = int(sys.argv[3+num_algos])
	sparsities = []

	for i in range(num_sparsities):
		sparsity = sys.argv[4+num_algos+i]
		sparsities.append(sparsity)

	# Read the name of the results file
	results_fname = sys.argv[4+num_algos+num_sparsities]

	env_details = sys.argv[5+num_algos+num_sparsities]
	
	# Define part of the plot-title depending on the sparsity pattern
	title = makeTitle(sparsity_pattern)

 
	if DEBUG:
		print(sparsity_pattern, algos, sparsities, labels)
  
	# Create the plot
	plot_comparison(algos, sparsities, sparsity_pattern, labels, title, results_fname, env_details)
    
    

if __name__ == '__main__':
	sys.exit(main())


