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

#set env path to root directory ?? for python liibrary function to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
# from plotslib.plot_utils import getPlotsDirectory, directoriesFromTime
	

def plot_comparison(title, fname = "rosko_comp"):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','k','r','r']	
	# labels = ['Rosko', 'CSR-Numpy', 'Array-Numpy', 'Naive']
	labels = ['Rosko', 'Array-Numpy']
    # algos = ['rosko', 'numpy_csr', 'numpy_arr']
	algos = ['rosko', 'numpy_arr']
	sparsities = [60, 70, 80, 90, 95, 98, 99]
	# sparsity = [99, 99.5, 99.8, 99.9]
	results_fname = 'results_comp_numpy_random_sample'
	dft = pandas.read_csv(results_fname)
	# runs = dft['runs'].iloc[0]

	# create results folders if not there and put plots in them, and get time
	# file_path = Path('./' + results_fname)
	# creation_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
	# plotsDir, dateStr = directoriesFromTime(creation_datetime, os.getcwd())
	
	
	plt.figure(figsize = (6,4))
	for i in range(len(algos)):
		algo_time = dft[dft['algo'] == algos[i]]['time'].values
		plt.plot(sparsities, algo_time, label = labels[i], marker = markers[i], color = colors[i])
		
	
	plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('SpMM runtime at various sparsities on Intel i5,\nusing ' + title, fontsize = 24)
	plt.xlabel("Sparsity (%)", fontsize = 24)
	plt.ylabel("Runtime (sec)", fontsize = 24)
	plt.yticks( fontsize = 20)
	plt.legend(loc = "upper right", prop={'size': 14})
	plt.savefig("%s_perf.pdf" % (fname), bbox_inches='tight')
	# plt.savefig("%s%s_%s_r%s_perf.pdf" % (plotsDir, dateStr, fname, runs), bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#

def main(typeComp):
	if typeComp=='random-uniform':
		plot_comparison("random uniform sparse matrices")
	elif typeComp=='row-pattern':
		plot_comparison("row-pattern sparse matrices")
	elif typeComp=='diagonal':
		plot_comparison("diagonal pattern sparse matrices")
	else:
		print(typeComp + " is not a valid type of sparsity pattern\n")

if __name__ == '__main__':
	_, typeComp = sys.argv
	main(typeComp)


