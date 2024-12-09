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
# FYI: currently markers and colors only allow for 5 algorithms in one plot, each with a distinctive marker and color
ALLOWED_ALGOS_WITH_LABEL =  {'numpy_csr':'CSR-Numpy'}
ALLOWED_SPARSITY_PATTERNS = ['random-uniform', 
                             'row-pattern', 
                             'diagonal', 
                             'column-pattern'] # If changed, then update makeTitle()

DEBUG = False

#set env path to root directory ?? for python liibrary function to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plotslib.plot_utils import getPlotsDirectory, directoriesFromTime
	

def plot_comparison(algos, sparsities, sparsity_pattern, title, results_fname, env_details, bits, fname = "plot_bits"):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','k','r','r']
	dft = pandas.read_csv(results_fname)
	# runs = dft['runs'].iloc[0]

	# create results folders if not there and put plots in them, and get time
	file_path = Path('./' + results_fname)
	creation_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
	plotsDir, dateStr = directoriesFromTime(creation_datetime, os.getcwd())
	
	
	plt.figure(figsize = (6,4))
	for i in range(len(bits)):
		print('hehe')
		algo_time = dft[dft['bits'] == bits[i]]['time'].values
		algo_sparsities = dft[dft['bits'] == bits[i]]['sp'].values
		plt.plot(algo_sparsities, algo_time / (100-algo_sparsities), label = str(bits[i]) + ' bits', marker = markers[i], color = colors[i])
		
	
	plt.title('Numpy dense 32 VS 64 bit floats', fontsize = 24)
	plt.xlabel("Sparsity (%)", fontsize = 16)
	plt.ylabel("Running time / density", fontsize = 16)
	plt.xticks(np.asarray(sparsities, dtype=float), fontsize=10)
	plt.yticks( fontsize = 10)
	plt.legend(loc = "center right", prop={'size': 12})
	plt.savefig("%s%s_%s_%s.pdf" % (plotsDir, dateStr, fname, env_details), bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	
 
 
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
		print(sparsity_pattern + " is not a valid type of sparsity pattern\n")
		sys.exit()

	return title


def main():
    
	if DEBUG: print(sys.argv)
 
    # Read the type of sparsity pattern from input
	sparsity_pattern = sys.argv[1]
	if sparsity_pattern not in ALLOWED_SPARSITY_PATTERNS:
		print(sparsity_pattern + " is not a valid type of sparsity pattern\n")
		sys.exit()

	# Read the algorithms used in the experiment and write them in algos array
	num_algos = int(sys.argv[2])
	algos = []

	for i in range(num_algos):
		algo = sys.argv[3+i]
		if algo not in ALLOWED_ALGOS_WITH_LABEL.keys():
			print(algo + " is not a valid algorithm\n")
			sys.exit()
		algos.append(algo)

	bits = [32, 64]

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
		print(sparsity_pattern, algos, sparsities)
  
	# Create the plot
	plot_comparison(algos, sparsities, sparsity_pattern, title, results_fname, env_details, bits)
    
    

if __name__ == '__main__':
	sys.exit(main())


