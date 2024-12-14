import pandas
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cm as cm
import matplotlib as mpl
import numpy as np
import datetime
import os
import re
import sys
from pathlib import Path
from matplotlib import ticker as mticker
from matplotlib.ticker import MaxNLocator
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata



# GLOBAL VARIABLES
ALLOWED_SPARSITY_PATTERNS = ['random-uniform', 
                             'row-pattern', 
                             'diagonal', 
                             'column-pattern'] # If changed, then update makeTitle()

DEBUG = False

#set env path to root directory ?? for python liibrary function to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plotslib.plot_utils import getPlotsDirectory, directoriesFromTime


def plot_3D_constant_N(sparsity_patterns, sparsities, ps, n, titles, results_fname, env_details, fname = "plot_p_3D_constant_N", time_type="rosko-time"):
    plt.rcParams.update({'font.size': 12})
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
        nrows, ncols = num_sppatterns, 1

    # Determine min and max runtime values to later fix the Z-axis for all subplots
    sparsities_min = round(float(min(sparsities)), 1)
    sparsities_max = round(float(max(sparsities)), 1)
    ps_min = min(int(p) for p in ps)
    ps_max = max(int(p) for p in ps)
    filter = (dft['algo'] == 'rosko') & (dft['N'] == n) & \
             (round(dft['sp'], 1) >= sparsities_min) & \
             (round(dft['sp'], 1) <= sparsities_max) & \
             (dft['p'] >= ps_min) & \
             (dft['p'] <= ps_max)
    min_runtime = dft[filter]['rosko-time'].min()
    max_runtime = dft[filter]['rosko-time'].max()

    # Create subplots
    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(7 * ncols + 5, 7 * nrows), 
        layout = 'constrained', 
        subplot_kw={'projection': '3d'}
    )
 
    axes = np.array(axes).flatten()  # Flatten in case of a 2D grid for easier indexing
    

    for i_spp in range(len(sparsity_patterns)):
        constants_filter = filter & (dft['sppattern'] == sparsity_patterns[i_spp])
        rosko_ps = dft[constants_filter]['p']
        rosko_sps = dft[constants_filter]['sp']
        rosko_times = dft[constants_filter][time_type]

        if DEBUG:
            print(dft.dtypes)
            print(rosko_ps)
            print(rosko_sps)
            print(rosko_times)

        # Grid formatting specifically for plot_surface arguments
        x1 = np.linspace(rosko_ps.min(), rosko_ps.max(), len(rosko_ps.unique()))
        y1 = np.linspace(rosko_sps.min(), rosko_sps.max(), len(rosko_sps.unique()))
        x2, y2 = np.meshgrid(x1, y1)
        z2 = griddata((rosko_ps, rosko_sps), rosko_times, (x2, y2), method='cubic')
        
        # Plot the surface plot with the datapoints in (surface + scatter)
        ax = axes[i_spp]
        # surf = ax.plot_trisurf(rosko_ps.values, rosko_sps.values, rosko_times.values, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)
        surf = ax.plot_surface(x2, y2, z2, rstride=1, cstride=1, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime, alpha=0.5)
        surf = ax.scatter3D(rosko_ps.values, rosko_sps.values, rosko_times.values, alpha = 0.9, c=(rosko_times.values), cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)
        ax.plot(rosko_ps.values, rosko_sps.values, 'k.', zdir='z', zs=min_runtime, alpha=0.2)
        ax.contourf(x2, y2, z2,zdir='z', offset=min_runtime, cmap=cm.jet_r, alpha=0.2,  vmin=min_runtime, vmax=max_runtime)

        # Add subplot-specific title and labels and more
        title = titles[i_spp]
        official_title = title[0].title() + title[1 :]
        ax.set_title(f"{official_title}", fontsize=14, pad=2)
        ax.set_xlabel("Threads (p)")
        ax.set_xlim(ps_min, ps_max)
        # ax.set_xticks(np.arange(ps_min, ps_max+1, 20.0))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_ylabel("Sparsity [%]")
        ax.set_yticks(np.arange(sparsities_min, sparsities_max+1, 10.0))
        # ax.set_yticks(np.asarray(sparsities, dtype=float))
        ax.invert_yaxis()
        # ax.set_yticks(np.asarray(sparsities, dtype=float))
        ax.set_zlabel("Running time [sec]")
        ax.set_zlim(min_runtime, max_runtime)
        ax.view_init(18,-32)
        


    # Add a single, shared color bar on the right side of all plots
    fig.colorbar(surf, ax=axes[:], location='right', shrink=0.3, label="Running time [sec]")

    # Add the title for the whole figure
    # official_suptitle = "3D Running time Surface Plots for Rosko, for Different Sparsity Patterns and N=" + str(n)
    official_suptitle = "3D running time surface plots for Rosko, for different sparsity patterns on Intel-i5"
    # official_suptitle = "3D running time surface plots for Rosko, for different sparsity patterns on Intel-i7"
    fig.suptitle(official_suptitle, fontsize=16)
    # fig.align_labels()  # same as fig.align_xlabels(); fig.align_ylabels()
    # fig.align_titles()

    # Save the figure
    fig.savefig("%s%s_%s_%s_perf.pdf" % (plotsDir, dateStr, fname, env_details), bbox_inches='tight', pad_inches=0.8)
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

def closest(lst, val):
     
    # return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-val))]
    lst = np.array(lst, dtype=float)
    idx = (np.abs(lst - val)).argmin()
    return lst[idx]

# def inc(value):
#     current = value[0]
#     # print(current)
#     value[0] += 1
#     return current


# def main():
#     if DEBUG: print(sys.argv)

#     # Read the sparsity patterns used in the experiment and write them in sparsity_patterns array
#     num_sparsity_patterns = int(sys.argv[1])
#     sparsity_patterns = []

#     for i in range(num_sparsity_patterns):
#         sparsity_pattern = sys.argv[2+i]
#         if sparsity_pattern not in ALLOWED_SPARSITY_PATTERNS:
#             raise ValueError(f"Sparsity pattern '{sparsity_pattern}' is not allowed.")
#             sys.exit()
#         sparsity_patterns.append(sparsity_pattern)


#     # Read the sparsity values used in experiment and write them in sparsities array
#     num_sparsities = int(sys.argv[2+num_sparsity_patterns])
#     sparsities = []

#     for i in range(num_sparsities):
#         sparsity = sys.argv[3+num_sparsity_patterns+i]
#         sparsities.append(sparsity)
		
#     # Read the core values used in experiment and write them in ps array
#     num_ps = int(sys.argv[3+num_sparsity_patterns+num_sparsities])
#     ps = []

#     for i in range(num_ps):
#         p = sys.argv[4+num_sparsity_patterns+num_sparsities+i]
#         ps.append(p)


#     # Read the the n-parameters necessary to compute the list of ns
#     n_start = int(sys.argv[4+num_sparsity_patterns+num_sparsities+num_ps])

#     n_end = int(sys.argv[5+num_sparsity_patterns+num_sparsities+num_ps])

#     n_step = int(sys.argv[6+num_sparsity_patterns+num_sparsities+num_ps])

#     ns = list(range(n_start, n_end+1, n_step))


#     # Read the name of the results file
#     results_fname = sys.argv[7+num_sparsity_patterns+num_sparsities+num_ps]
	
#     # Read the environment details, containing hyperthreading and user info
#     env_details = sys.argv[8+num_sparsity_patterns+num_sparsities+num_ps]
	
#     # Define part of the plot-title depending on the sparsity pattern
#     titles = []

#     for sppattern in sparsity_patterns:
#         titles.append(makeTitle(sppattern))

#     # CREATE 3D PLOTS

#     sparsity = closest(sparsities, 90.0) # Choose the value in sparsities that is cloest to 90% sparsity as constant for 3D plot

#     if DEBUG:
#         print("Some of the inputs to plot_3D_constant_sparsity:")
#         print(sparsity_patterns, sparsity, ps, ns)

#     n = ns[len(ns)-1] # Use the largest n as constant for 3D plot
	
#     if DEBUG:
#         print("Some of the inputs to plot_3D_constant_N:")
#         print(sparsity_patterns, sparsities, ps, n)    

    # plot_3D_constant_N(sparsity_patterns, sparsities, ps, n, titles, results_fname, env_details)

def inc(value):
    current = value[0]
    value[0] += 1
    return current


def main():
    if DEBUG: 
        print(sys.argv)

    # Initialize a mutable counter
    j = [1]  # Start at 1, since `sys.argv[0]` is the script name.

    # Read the sparsity patterns used in the experiment
    num_sparsity_patterns = int(sys.argv[inc(j)])
    sparsity_patterns = []

    for i in range(num_sparsity_patterns):
        sparsity_pattern = sys.argv[inc(j)]
        if sparsity_pattern not in ALLOWED_SPARSITY_PATTERNS:
            raise ValueError(f"Sparsity pattern '{sparsity_pattern}' is not allowed.")
            sys.exit()
        sparsity_patterns.append(sparsity_pattern)

    # Read the sparsity values
    num_sparsities = int(sys.argv[inc(j)])
    sparsities = []

    for i in range(num_sparsities):
        sparsity = sys.argv[inc(j)]
        sparsities.append(sparsity)

    # Read the core values
    num_ps = int(sys.argv[inc(j)])
    ps = []

    for i in range(num_ps):
        p = sys.argv[inc(j)]
        ps.append(p)

    # Read the n-parameters
    n_start = int(sys.argv[inc(j)])
    n_end = int(sys.argv[inc(j)])
    n_step = int(sys.argv[inc(j)])
    ns = list(range(n_start, n_end + 1, n_step))

    # Read the name of the results file
    results_fname = sys.argv[inc(j)]

    # Read the environment details
    env_details = sys.argv[inc(j)]

    # Read cache size factors
    L3_factors_length = int(sys.argv[inc(j)])
    L3_factors = []
    for i in range(L3_factors_length):
        L3_factors.append(sys.argv[inc(j)])

    plot_p_or_sp = sys.argv[inc(j)]

    # Define part of the plot-title depending on the sparsity pattern
    titles = [makeTitle(sppattern) for sppattern in sparsity_patterns]

    # CREATE 3D PLOTS

    sparsity = closest(sparsities, 90.0)  # Choose the value in sparsities closest to 90% sparsity

    if DEBUG:
        print("Some of the inputs to plot_3D_constant_sparsity:")
        print(sparsity_patterns, sparsity, ps, ns)

    n = ns[-1]  # Use the largest n as constant for the 3D plot

    if DEBUG:
        print("Some of the inputs to plot_3D_constant_N:")
        print(sparsity_patterns, sparsities, ps, n)
    
    plot_3D_constant_N(sparsity_patterns, sparsities, ps, n, titles, results_fname, env_details)



if __name__ == '__main__':
	sys.exit(main())


