import pandas
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cm as cm
# import matplotlib as mpl
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


def plot_3D_cache_sp(
        plot_type,
        L3_factors,
        sparsity_patterns,
        sparsities,
        ps,
        n,
        titles,
        results_fname,
        env_details,
        fname = "plot_p_3D_wehweh",
        time_type="rosko-time"
    ):
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
    L3_factor_min = round(float(min(L3_factors)), 1)
    L3_factor_max = round(float(max(L3_factors)), 1)

    comparison_elem_min = int(min(ps)) if plot_type == 'p' else round(float(min(sparsities)), 1)
    comparison_elem_max = int(max(ps)) if plot_type == 'p' else round(float(max(sparsities)), 1)

    filter = (dft['algo'] == 'rosko') & (dft['N'] == n) & \
             (dft['L3_factor'] >= L3_factor_min) & \
             (dft['L3_factor'] <= L3_factor_max) & \
             (dft[plot_type] >= comparison_elem_min) & \
             (dft[plot_type] <= comparison_elem_max)
    
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

        rosko_L3_factor = dft[constants_filter]['L3_factor']
        rosko_comparison_elem = dft[constants_filter]['p'] if plot_type == 'p' else dft[constants_filter]['sp']
        rosko_times = dft[constants_filter][time_type]

        if len(rosko_L3_factor) == 0 or len(rosko_comparison_elem) == 0 or len(rosko_times) == 0:
            print(f"\nSkipping plot for sparsity pattern '{sparsity_patterns[i_spp]}' due to insufficient data.")
            print('L3 ', len(rosko_L3_factor), 'rosko times: ', len(rosko_times), 'other: ', len(rosko_comparison_elem))
            continue

        if DEBUG:
            print(dft.dtypes)
            print(rosko_L3_factor)
            print(rosko_comparison_elem)
            print(rosko_times)

        # Grid formatting specifically for plot_surface arguments
        x1 = np.linspace(rosko_L3_factor.min(), rosko_L3_factor.max(), len(rosko_L3_factor.unique()))
        y1 = np.linspace(rosko_comparison_elem.min(), rosko_comparison_elem.max(), len(rosko_comparison_elem.unique()))
        x2, y2 = np.meshgrid(x1, y1)
        z2 = griddata((rosko_L3_factor, rosko_comparison_elem), rosko_times, (x2, y2), method='cubic')
        
        # Plot the surface plot with the datapoints in (surface + scatter)
        ax = axes[i_spp]
        # surf = ax.plot_trisurf(rosko_L3_factor.values, rosko_comparison_elem.values, rosko_times.values, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)
        surf = ax.plot_surface(x2, y2, z2, rstride=1, cstride=1, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime, alpha=0.5)
        surf = ax.scatter3D(rosko_L3_factor.values, rosko_comparison_elem.values, rosko_times.values, alpha = 0.9, c=(rosko_times.values), cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)
        
        ax.plot(rosko_L3_factor.values, rosko_comparison_elem.values, 'k.', zdir='z', zs=min_runtime, alpha=0.2)
        ax.contourf(x2, y2, z2,zdir='z', offset=min_runtime, cmap=cm.jet_r, alpha=0.2,  vmin=min_runtime, vmax=max_runtime)

        # Add subplot-specific title and labels and more
        title = titles[i_spp]
        official_title = title[0].title() + title[1 :]

        ax.set_title(f"{official_title}", fontsize=14, pad=2)
        ax.set_xlabel("L3 multiply factor")
        ax.set_xlim(L3_factor_min, L3_factor_max)
        # ax.set_xticks(np.arange(L3_factor_min, L3_factor_max+1, 1.0)) 
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        ylabel = "Sparsity [%]" if plot_type == 'sp' else "p"
        ax.set_ylabel(ylabel)

        ax.set_yticks(np.arange(comparison_elem_min, comparison_elem_max+1, 10.0))
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
        sparsity = float(sys.argv[inc(j)])
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
        L3_factors.append(float(sys.argv[inc(j)]))

    plot_type = sys.argv[inc(j)]

    # Define part of the plot-title depending on the sparsity pattern
    titles = [makeTitle(sppattern) for sppattern in sparsity_patterns]

    # CREATE 3D PLOTS

    sparsity = closest(sparsities, 90.0)  # Choose the value in sparsities closest to 90% sparsity

    if DEBUG:
        print("Some of the inputs to plot_3D_constant_sparsity:")
        print(sparsity_patterns, sparsity, ps, ns)

    n = ns[-1]  # Use the largest n as constant for the 3D plot

    if DEBUG:
        print("Some of the inputs to plot_3D:")
        print(sparsity_patterns, sparsities, ps, n)
    
    plot_3D_cache_sp(plot_type, L3_factors,sparsity_patterns, sparsities, ps, n, titles, results_fname, env_details)
         



if __name__ == '__main__':
	sys.exit(main())


