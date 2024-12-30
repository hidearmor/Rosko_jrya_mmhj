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
                             'numpy_arr':'NumPy-Dense', 
                             'numpy_csr':'NumPy-CSR', 
                             'naive':'Naive', 
                             'numpy_dense':'NumPy-Dense, zeros stripped', 
                             'numpy_dia':'NumPy-Diagonal'}
ALLOWED_SPARSITY_PATTERNS = ['random-uniform',
                             'row-pattern', 
                             'diagonal', 
                             'column-pattern'] # If changed, then update makeTitle()

DEBUG = False

#set env path to root directory ?? for python liibrary function to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plotslib.plot_utils import getPlotsDirectory, directoriesFromTime
	

def plot_comparison(p_values, algos, sparsities, sparsity_pattern, labels, title, results_fname, results_baseline_fname, env_details, fname = "plot_comp"):
	plt.rcParams.update({'font.size': 12})
	# markers = ['o','v','s','d','^']
	# colors = ['b','g','k','r','r']
	markers = ['o', 'v', 's', 'd', '^', 'p', '*', 'h', 'x', '+']
	colors = ['b', 'g', 'k', 'r', 'c', 'm', 'y', 'orange', 'purple', 'brown']
	# runs = dft['runs'].iloc[0]


	# create results folders if not there and put plots in them, and get time
	file_path = Path('./' + results_fname)
	creation_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
	plotsDir, dateStr = directoriesFromTime(creation_datetime, os.getcwd())
	
	print(p_values)
	# return
	plt.figure(figsize = (6,4))

	# plot the NumPy dia from results_baseline_fname
	dft = pandas.read_csv(results_baseline_fname)
	max_sp = float(max(sparsities))
	min_sp = float(min(sparsities))
	algo_time = dft[(dft['algo'] == 'numpy_arr') & (dft['sppattern'] == sparsity_pattern) & (dft['sp'] < max_sp) & (dft['sp'] >= min_sp)]['time'].values
	algo_sparsities = dft[(dft['algo'] == 'numpy_arr') & (dft['sppattern'] == sparsity_pattern) & (dft['sp'] < max_sp) & (dft['sp'] >= min_sp)]['sp'].values
	plt.plot(algo_sparsities, algo_time, label = 'NumPy-Dense', marker = markers[0], color = colors[0])

	dft = pandas.read_csv(results_fname)
	for i in range(len(p_values)):
		p = int(p_values[i])
		max_sp = float(max(sparsities))
		min_sp = float(min(sparsities))
		algo_time = dft[(dft['p'] == p) & (dft['sppattern'] == sparsity_pattern) & (dft['sp'] < max_sp) & (dft['sp'] >= min_sp)]['rosko-time'].values
		algo_sparsities = dft[(dft['p'] == p) & (dft['sppattern'] == sparsity_pattern) & (dft['sp'] < max_sp) & (dft['sp'] >= min_sp)]['sp'].values
		plt.plot(algo_sparsities, algo_time, label = makeLabel(p), marker = markers[i+1], color = colors[i+1])

	
	# plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('(b) SDMM on Intel Core i7 using\n' + title, fontsize = 18 )
	# plt.title('(a) SDMM on Intel Core i5 using\n' + title, fontsize = 18 )
	plt.title(title, fontsize = 18 )
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
	return "Rosko with varying threads p and NumPy-Dense\nusing random-uniform input on Intel Core i5 "

def makeLabel(p):
	return 'p = ' + str(p)

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

	# Read the sparsity values used in experiment and write them in sparsities array
	num_sparsities = int(sys.argv[3+num_algos])
	sparsities = []

	for i in range(num_sparsities):
		sparsity = sys.argv[4+num_algos+i]
		sparsities.append(sparsity)

	# Read the name of the results file
	results_fname = sys.argv[4+num_algos+num_sparsities]

	results_baseline_fname = sys.argv[5+num_algos+num_sparsities]

	env_details = sys.argv[6+num_algos+num_sparsities]

	num_p_values = int(sys.argv[7+num_algos+num_sparsities])
	p_values = []

	for i in range(num_p_values):
		p = sys.argv[i + 8 + num_algos + num_sparsities]
		p_values.append(p)

	
	# Define part of the plot-title depending on the sparsity pattern
	title = makeTitle(sparsity_pattern)

 
	if DEBUG:
		print(sparsity_pattern, algos, sparsities, labels)
  
	# Create the plot
	plot_comparison(p_values, algos, sparsities, sparsity_pattern, labels, title, results_fname, results_baseline_fname, env_details)
    
    

if __name__ == '__main__':
	sys.exit(main())


