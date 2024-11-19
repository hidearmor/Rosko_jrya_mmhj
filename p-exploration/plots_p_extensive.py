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
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata



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

def plot_3D_constant_sparsity(sparsity_patterns, sparsity, ps, ns, titles, results_fname, env_details, fname = "plot_p_3D_constant_sparsity", time_type="rosko-time"):
    plt.rcParams.update({'font.size': 12})
    markers = ['o', 'v', 's', 'd', '^', 'p', '*', 'h', 'x', '+']
    colors = ['b', 'g', 'k', 'r', 'c', 'm', 'y', 'orange', 'purple', 'brown']
    dft = pandas.read_csv(results_fname)

    # create results folders if not there and put plots in them, and get time
    file_path = Path('./' + results_fname)
    creation_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
    plotsDir, dateStr = directoriesFromTime(creation_datetime, os.getcwd())

    if DEBUG:
         print(creation_datetime)
         print(plotsDir)
         print(dateStr)

    # Determine subplot grid layout based on number of patterns
    num_sppatterns = len(sparsity_patterns)

    if num_sppatterns == 2:
        nrows, ncols = 1, 2
    elif num_sppatterns == 4:
        nrows, ncols = 2, 2
    else:
        nrows, ncols = 1, num_sppatterns

    # Determine min and max runtime values to later fix the Z-axis for all subplots
    sparsity = float(sparsity)
    filter = (dft['algo'] == 'rosko') & (dft['sp'] == sparsity)
    min_runtime = dft[filter]['rosko-time'].min()
    max_runtime = dft[filter]['rosko-time'].max()

    # Create subplots
    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(7 * ncols + 5, 7 * nrows),  # Increase figure size for more room
        layout = 'constrained', 
        subplot_kw={'projection': '3d'}
    )
 
    axes = np.array(axes).flatten()  # Flatten in case of a 2D grid for easier indexing
    

    for i_spp in range(len(sparsity_patterns)):
        constants_filter = (dft['algo'] == 'rosko') & (dft['sp'] == sparsity) & (dft['sppattern'] == sparsity_patterns[i_spp])
        rosko_ps = dft[constants_filter]['p'].values
        rosko_ns = dft[constants_filter]['N'].values
        rosko_times = dft[constants_filter][time_type].values

        x1 = np.linspace(dft[constants_filter]['p'].min(), dft[constants_filter]['p'].max(), len(dft[constants_filter]['p'].unique()))
        y1 = np.linspace(dft[constants_filter]['N'].min(), dft[constants_filter]['N'].max(), len(dft[constants_filter]['N'].unique()))
        x2, y2 = np.meshgrid(x1, y1)
        z2 = griddata((dft[constants_filter]['p'], dft[constants_filter]['N']), dft[constants_filter][time_type], (x2, y2), method='cubic')

        # Plot the surface
        ax = axes[i_spp]
        # surf = ax.plot_trisurf(rosko_ps, rosko_ns, rosko_times, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)
        # surf = ax.plot_surface(rosko_ps, rosko_ns, rosko_times, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)
        surf = ax.plot_surface(x2, y2, z2, rstride=1, cstride=1, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime, alpha=0.7)
        surf = ax.scatter3D(rosko_ps, rosko_ns, rosko_times, alpha = 0.8, c=(rosko_times), cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)

        # Add subplot-specific title and labels
        title = titles[i_spp]
        official_title = title[0].title() + title[1 :]
        ax.set_title(f"{official_title}", fontsize=14, pad=2)
        ax.set_xlabel("Threads (p)")
        ax.set_ylabel("N")
        ax.set_zlabel("Runtime (sec)")
        ax.set_zlim(min_runtime, max_runtime)

        if DEBUG:
            #   print(dft.dtypes)
              print(rosko_ps)
              print(rosko_ns)
              print(rosko_times)


    # Add a single, shared color bar on the right side of all plots
    # fig.subplots_adjust(right=0.85)  # Adjust main plot area to make room for color bar
    # cbar_ax = fig.add_axes([0.95, 0.15, 0.02, 0.7])  # Position color bar to the right
    # cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    # fig.colorbar(surf, cax=cbar_ax, orientation='vertical', label="Runtime (sec)")
    # fig.colorbar(surf, ax=axes.ravel().tolist(), orientation='vertical', label="Runtime (sec)")
    # cbar = fig.colorbar(surf)
    # cbar.set_label(label="Runtime (sec)")

    # cax,kw = mpl.colorbar.make_axes([ax for ax in axes])
    # plt.colorbar(surf, cax=cax, **kw)

    fig.colorbar(surf, ax=axes[:], location='right', shrink=0.3)

    official_suptitle = "3D Runtime Surface Plots for Different Sparsity Patterns for " + str(sparsity) + "% sparsity"
    fig.suptitle(official_suptitle, fontsize=16)
    fig.align_labels()  # same as fig.align_xlabels(); fig.align_ylabels()
    fig.align_titles()
    # plt.tight_layout(rect=[0, 0, 1, 0.95])

    if DEBUG:
         print("%s%s_%s_%s_perf.pdf" % (plotsDir, dateStr, fname, env_details))
    fig.savefig("%s%s_%s_%s_perf.pdf" % (plotsDir, dateStr, fname, env_details), bbox_inches='tight', pad_inches=0.8)
    plt.show()
    plt.clf()
    plt.close('all')



def plot_3D_constant_N(sparsity_patterns, sparsities, ps, n, titles, results_fname, env_details, fname = "plot_p_3D_constant_N", time_type="rosko-time"):
    plt.rcParams.update({'font.size': 12})
    markers = ['o', 'v', 's', 'd', '^', 'p', '*', 'h', 'x', '+']
    colors = ['b', 'g', 'k', 'r', 'c', 'm', 'y', 'orange', 'purple', 'brown']
    dft = pandas.read_csv(results_fname)

    # create results folders if not there and put plots in them, and get time
    file_path = Path('./' + results_fname)
    creation_datetime = datetime.datetime.fromtimestamp(file_path.stat().st_ctime)
    plotsDir, dateStr = directoriesFromTime(creation_datetime, os.getcwd())

    if DEBUG:
         print(creation_datetime)
         print(plotsDir)
         print(dateStr)

    # Determine subplot grid layout based on number of patterns
    num_sppatterns = len(sparsity_patterns)

    if num_sppatterns == 2:
        nrows, ncols = 1, 2
    elif num_sppatterns == 4:
        nrows, ncols = 2, 2
    else:
        nrows, ncols = 1, num_sppatterns

    # Determine min and max runtime values to later fix the Z-axis for all subplots
    filter = (dft['algo'] == 'rosko') & (dft['N'] == n)
    min_runtime = dft[filter]['rosko-time'].min()
    max_runtime = dft[filter]['rosko-time'].max()

    # Create subplots
    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(7 * ncols + 5, 7 * nrows),  # Increase figure size for more room
        layout = 'constrained', 
        subplot_kw={'projection': '3d'}
    )
 
    axes = np.array(axes).flatten()  # Flatten in case of a 2D grid for easier indexing
    

    for i_spp in range(len(sparsity_patterns)):
        constants_filter = (dft['algo'] == 'rosko') & (dft['N'] == n) & (dft['sppattern'] == sparsity_patterns[i_spp])
        rosko_ps = dft[constants_filter]['p'].values
        rosko_sps = dft[constants_filter]['sp'].values
        rosko_times = dft[constants_filter][time_type].values

        if DEBUG:
            #   print(dft.dtypes)
              print(rosko_ps)
              print(rosko_sps)
              print(rosko_times)

        x1 = np.linspace(dft[constants_filter]['p'].min(), dft[constants_filter]['p'].max(), len(dft[constants_filter]['p'].unique()))
        y1 = np.linspace(dft[constants_filter]['sp'].min(), dft[constants_filter]['sp'].max(), len(dft[constants_filter]['sp'].unique()))
        x2, y2 = np.meshgrid(x1, y1)
        z2 = griddata((dft[constants_filter]['p'], dft[constants_filter]['sp']), dft[constants_filter][time_type], (x2, y2), method='cubic')

        # Plot the surface
        ax = axes[i_spp]
        # surf = ax.plot_trisurf(rosko_ps, rosko_sps, rosko_times, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)
        # surf = ax.plot_surface(rosko_ps, rosko_sps, rosko_times, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)
        surf = ax.plot_surface(x2, y2, z2, rstride=1, cstride=1, cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime, alpha=0.7)
        surf = ax.scatter3D(rosko_ps, rosko_sps, rosko_times, alpha = 0.8, c=(rosko_times), cmap=cm.jet_r, linewidth=0.1, vmin=min_runtime, vmax=max_runtime)

        # Add subplot-specific title and labels
        title = titles[i_spp]
        official_title = title[0].title() + title[1 :]
        ax.set_title(f"{official_title}", fontsize=14, pad=2)
        ax.set_xlabel("Threads (p)")
        ax.set_ylabel("Sparsity (sp)")
        ax.set_zlabel("Runtime (sec)")
        ax.set_zlim(min_runtime, max_runtime)



    # Add a single, shared color bar on the right side of all plots
    # fig.subplots_adjust(right=0.85)  # Adjust main plot area to make room for color bar
    # cbar_ax = fig.add_axes([0.95, 0.15, 0.02, 0.7])  # Position color bar to the right
    # cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    # fig.colorbar(surf, cax=cbar_ax, orientation='vertical', label="Runtime (sec)")
    # fig.colorbar(surf, ax=axes.ravel().tolist(), orientation='vertical', label="Runtime (sec)")
    # cbar = fig.colorbar(surf)
    # cbar.set_label(label="Runtime (sec)")

    # cax,kw = mpl.colorbar.make_axes([ax for ax in axes])
    # plt.colorbar(surf, cax=cax, **kw)

    fig.colorbar(surf, ax=axes[:], location='right', shrink=0.3)

    official_suptitle = "3D Runtime Surface Plots for Different Sparsity Patterns for N=" + str(n)
    fig.suptitle(official_suptitle, fontsize=16)
    fig.align_labels()  # same as fig.align_xlabels(); fig.align_ylabels()
    fig.align_titles()
    # plt.tight_layout(rect=[0, 0, 1, 0.95])

    if DEBUG:
         print("%s%s_%s_%s_perf.pdf" % (plotsDir, dateStr, fname, env_details))
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

    sparsity = sparsities[len(sparsities)-1] # Use the largest sparsity as constant for 3D plot

    if DEBUG:
        print("Some of the inputs to plot_3D_constant_sparsity:")
        print(sparsity_patterns, sparsity, ps, ns)

    plot_3D_constant_sparsity(sparsity_patterns, sparsity, ps, ns, titles, results_fname, env_details)
	
	# Create 3D plot
    n = ns[len(ns)-1] # Use the largest n as constant for 3D plot
	
    if DEBUG:
        print(sparsity_patterns, sparsities, ps, n)    

    plot_3D_constant_N(sparsity_patterns, sparsities, ps, n, titles, results_fname, env_details)
    
    

if __name__ == '__main__':
	sys.exit(main())


