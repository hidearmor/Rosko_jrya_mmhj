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
                             'numpy_arr':'Array-Numpy', 
                             'numpy_csr':'CSR-Numpy', 
                             'naive':'Naive', 
                             'numpy_dense':'Array-Numpy, zeros stripped', 
                             'numpy_dia':'Diagonal-Numpy'}
ALLOWED_SPARSITY_PATTERNS = ['random-uniform', 
                             'row-pattern', 
                             'diagonal', 
                             'column-pattern'] # If changed, then update makeTitle()

DEBUG = True

#set env path to root directory ?? for python liibrary function to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plotslib.plot_utils import getPlotsDirectory, directoriesFromTime
	

def plot_comparison(algos, sparsities, sparsity_pattern, labels, title, results_fname, env_details, ns, fname = "plot_comp_varyN"):
	plt.rcParams.update({'font.size': 12})
	# markers = ['o','v','s','d','^']
	# colors = ['b','g','k','r','r']
	markers = ['o', 'v', 's', 'd', '^', 'p', '*', 'h', 'x', '+']
	colors = ['b', 'g', 'k', 'r', 'c', 'm', 'y', 'orange', 'purple', 'brown']
	dft = pandas.read_csv(results_fname)
	# runs = dft['runs'].iloc[0]

	# create results folders if not there and put plots in them, and get time
	file_path = Path('./' + results_fname)
	creation_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
	plotsDir, dateStr = directoriesFromTime(creation_datetime, os.getcwd())
	
	
	plt.figure(figsize = (6,4))
	for i in range(len(sparsities)):
		for j in range(len(algos)):
			algo_time = dft[(dft['algo'] == algos[j]) & (round(dft['sp']) == int(sparsities[i]))]['time'].values
			plt.plot(ns, algo_time, label = ("%s, %s%%" % (labels[j], sparsities[i])), marker = markers[i], color = colors[j])
	

	# plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('SpMM runtime at various N,\nusing ' + title, fontsize = 18 )
	plt.xlabel("N", fontsize = 16)
	plt.ylabel("Runtime (sec)", fontsize = 16)
	plt.yticks( fontsize = 10)
	plt.xticks( fontsize = 10)
	# num_ticks = len(sparsities) # Number of x-ticks you want
	# plt.xticks(np.linspace(min(sparsities), max(sparsities), num_ticks), fontsize=10)
	# plt.xticks(np.asarray(sparsities, dtype=float), fontsize=10)
	plt.legend(loc = "upper right", prop={'size': 14})
	# plt.savefig("%s_perf.pdf" % (fname), bbox_inches='tight')
	# plt.savefig("%s%s_%s_r%s_perf.pdf" % (plotsDir, dateStr, fname, runs), bbox_inches='tight')
	plt.savefig("%s%s_%s_%s_%s_perf.pdf" % (plotsDir, dateStr, fname, sparsity_pattern, env_details), bbox_inches='tight')
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


def makeLabels(algos):
    
    labels = []
    
    for algo in algos:
        labels.append(ALLOWED_ALGOS_WITH_LABEL[algo])
    
    return labels


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

	# Read the sparsity values used in experiment and write them in sparsities array
	num_sparsities = int(sys.argv[3+num_algos])
	sparsities = []

	for i in range(num_sparsities):
		sparsity = sys.argv[4+num_algos+i]
		sparsities.append(sparsity)

	# Read the name of the results file
	results_fname = sys.argv[4+num_algos+num_sparsities]

	env_details = sys.argv[5+num_algos+num_sparsities]

	n_start = int(sys.argv[6+num_algos+num_sparsities])

	n_end = int(sys.argv[7+num_algos+num_sparsities])

	n_step = int(sys.argv[8+num_algos+num_sparsities])

	ns = list(range(n_start, n_end+1, n_step))
	
	# Define part of the plot-title depending on the sparsity pattern
	title = makeTitle(sparsity_pattern)

	# Define the labels array based on the algorithms used in experiment
	labels = makeLabels(algos)
 
	if DEBUG:
		print(sparsity_pattern, algos, sparsities, ns, labels)
  
	# Create the plot
	plot_comparison(algos, sparsities, sparsity_pattern, labels, title, results_fname, env_details, ns)
    
    

if __name__ == '__main__':
	sys.exit(main())


