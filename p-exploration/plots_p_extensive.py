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
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D 


# GLOBAL VARIABLES
# FYI: currently markers and colors only allow for 10 algorithms in one plot, each with a distinctive marker and color
ALLOWED_ALGOS_WITH_LABEL =  {'rosko':'Rosko'}
ALLOWED_SPARSITY_PATTERNS = ['random-uniform', 
                             'row-pattern', 
                             'diagonal', 
                             'column-pattern'] # If changed, then update makeTitle()

DEBUG = True

#set env path to root directory ?? for python liibrary function to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plotslib.plot_utils import getPlotsDirectory, directoriesFromTime
	

def plot_3D(sparsity_patterns, sparsities, ps, n, titles, results_fname, env_details, fname = "plot_p_3D", time_type="rosko-time"):
    plt.rcParams.update({'font.size': 12})
    markers = ['o', 'v', 's', 'd', '^', 'p', '*', 'h', 'x', '+']
    colors = ['b', 'g', 'k', 'r', 'c', 'm', 'y', 'orange', 'purple', 'brown']
    dft = pandas.read_csv(results_fname)

    # create results folders if not there and put plots in them, and get time
    file_path = Path('./' + results_fname)
    creation_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
    plotsDir, dateStr = directoriesFromTime(creation_datetime, os.getcwd())

    # Determine subplot grid layout based on number of patterns
    num_sppatterns = len(sparsity_patterns)

    if num_sppatterns == 2:
        nrows, ncols = 1, 2
    elif num_sppatterns == 4:
        nrows, ncols = 2, 2
    else:
        nrows, ncols = 1, num_sppatterns

    # fig, axes = plt.subplots(nrows, ncols, figsize=(5 * len(sparsity_patterns), 5), subplot_kw={'projection': '3d'})
    # fig, axes = plt.subplots(nrows, ncols, figsize=(5 * nrows, 5 * ncols), subplot_kw={'projection': '3d'})
    
    # Determine min and max runtime values to later fix the Z-axis for all subplots
    filter = (dft['algo'] == 'rosko') & (dft['N'] == n)
    min_runtime = dft[filter]['rosko-time'].min()
    max_runtime = dft[filter]['rosko-time'].max()

    # Create subplots
    fig, axes = plt.subplots(
        nrows, ncols, 
        figsize=(5 * ncols, 5 * nrows),  # Increase figure size for more room
        subplot_kw={'projection': '3d'}
    )

    # Add spacing between subplots
    # fig.subplots_adjust(
    #     wspace=0.4,  # Add horizontal space between subplots
    #     hspace=2.0   # Add vertical space between rows
    # )

    axes = np.array(axes).flatten()  # Flatten in case of a 2D grid for easier indexing

    for i_spp in range(len(sparsity_patterns)):
        constants_filter = (dft['algo'] == 'rosko') & (dft['N'] == n) & (dft['sppattern'] == sparsity_patterns[i_spp])
        rosko_ps = dft[constants_filter]['p'].values
        rosko_sps = dft[constants_filter]['sp'].values
        rosko_times = dft[constants_filter][time_type].values

        # Plot the surface
        ax = axes[i_spp]
        surf = ax.plot_trisurf(rosko_ps, rosko_sps, rosko_times, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)

        # Add subplot-specific title and labels
        ax.set_title(f"{titles[i_spp]}", fontsize=14, pad=10)
        ax.set_xlabel("Threads (p)")
        ax.set_ylabel("Sparsity (sp)")
        ax.set_zlabel("Runtime (sec)")
        ax.set_zlim(min_runtime, max_runtime)
        # Add a color bar
        # fig.colorbar(surf, ax=ax, shrink=0.3, aspect=10, fraction=0.05, pad=0.2)
        # fig.colorbar(surf, ax=axes[i_spp], shrink=0.5, aspect=10)

        if DEBUG:
            #   print(dft.dtypes)
              print(rosko_ps)
              print(rosko_sps)
              print(rosko_times)

        # algo_time = dft[(dft['algo'] == algos[j]) & (round(dft['sp'], 1) == float(sparsities[i]))]['time'].values

    # Add a single, shared color bar on the right side of all plots
    fig.subplots_adjust(right=0.85)  # Adjust main plot area to make room for color bar
    cbar_ax = fig.add_axes([0.95, 0.15, 0.02, 0.7])  # Position color bar to the right
    fig.colorbar(surf, cax=cbar_ax, orientation='vertical', label="Runtime (sec)")
    # plt.title('SpMM runtime at various N,\nusing ' + title, fontsize = 18 )
    plt.suptitle("3D Runtime Surface Plots for Different Sparsity Patterns", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    # plt.xlabel("N", fontsize = 16)
    # plt.ylabel("Runtime (sec)", fontsize = 16)
    # plt.yticks( fontsize = 10)
    # plt.xticks( fontsize = 10)
    # num_ticks = len(sparsities) # Number of x-ticks you want
    # plt.xticks(np.linspace(min(sparsities), max(sparsities), num_ticks), fontsize=10)
    # plt.xticks(np.asarray(sparsities, dtype=float), fontsize=10)
    # plt.legend(loc = "upper left", prop={'size': 14})
    # plt.savefig("%s_perf.pdf" % (fname), bbox_inches='tight')
    # plt.savefig("%s%s_%s_r%s_perf.pdf" % (plotsDir, dateStr, fname, runs), bbox_inches='tight')
    plt.savefig("%s%s_%s_%s_perf.pdf" % (plotsDir, dateStr, fname, env_details), bbox_inches='tight')
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
		raise ValueError(f"Sparsity pattern '{sparsity_pattern}' is not allowed.")
		sys.exit()

	return title


def main():

    # python3 plots_p_extensive.py $num_sparsity_patterns ${sparsity_pattern[@]} $num_sparsity_values ${sparsity_values[@]} $num_ps ${ps[@]} $n_start $n_end $n_step FILE $nameHype

    if DEBUG: print(sys.argv)

    # Read the sparsity patterns used in the experiment and write them in sparsity_patterns array
    num_sparsity_patterns = int(sys.argv[1])
    sparsity_patterns = []

    for i in range(num_sparsity_patterns):
        sparsity_pattern = sys.argv[2+i]
        if sparsity_pattern not in ALLOWED_SPARSITY_PATTERNS:
            raise ValueError(f"Sparsity pattern '{sparsity_pattern}' is not allowed.")
            sys.exit()
        sparsity_patterns.append(sparsity_pattern)


    # Read the sparsity values used in experiment and write them in sparsities array
    num_sparsities = int(sys.argv[2+num_sparsity_patterns])
    sparsities = []

    for i in range(num_sparsities):
        sparsity = sys.argv[3+num_sparsity_patterns+i]
        sparsities.append(sparsity)
		
    # Read the core values used in experiment and write them in ps array
    num_ps = int(sys.argv[3+num_sparsity_patterns+num_sparsities])
    ps = []

    for i in range(num_ps):
        p = sys.argv[4+num_sparsity_patterns+num_sparsities+i]
        ps.append(p)


    # Read the the n-parameters necessary to compute the list of ns
    n_start = int(sys.argv[4+num_sparsity_patterns+num_sparsities+num_ps])

    n_end = int(sys.argv[5+num_sparsity_patterns+num_sparsities+num_ps])

    n_step = int(sys.argv[6+num_sparsity_patterns+num_sparsities+num_ps])

    ns = list(range(n_start, n_end+1, n_step))


    # Read the name of the results file
    results_fname = sys.argv[7+num_sparsity_patterns+num_sparsities+num_ps]
	
    # Read the environment details, containing hyperthreading and user info
    env_details = sys.argv[8+num_sparsity_patterns+num_sparsities+num_ps]
	
    # Define part of the plot-title depending on the sparsity pattern
    titles = []

    for sppattern in sparsity_patterns:
        titles.append(makeTitle(sppattern))


    if DEBUG:
        print(sparsity_patterns, sparsities, ps, ns)


    # Create the 4D plot
    # plot_4D(sparsity_patterns, sparsities, ps, ns, titles, results_fname, env_details)
	
	# Create 3D plot
    n = ns[len(ns)-1] # Use the largest n as constant for 3D plot
	
    if DEBUG:
        print(sparsity_patterns, sparsities, ps, n)    

    plot_3D(sparsity_patterns, sparsities, ps, n, titles, results_fname, env_details)
    
    

if __name__ == '__main__':
	sys.exit(main())


