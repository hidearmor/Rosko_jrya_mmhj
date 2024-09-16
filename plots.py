import pandas
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cm as cm
import numpy as np
import os
import re
import sys
from matplotlib import ticker as mticker

# pip install ssgetpy

# # Download SuiteSparse matrices
# python - <<END
# import ssgetpy
# ssgetpy.search(rowbounds=(5000,22000),colbounds=(5000,22000), \
#     dtype = 'real', group='ML_Graph').download(destpath = '.', extract=True)
# ssgetpy.search(nzbounds=(35631,35633),\
#     dtype = 'real', group='LPnetlib').download(destpath = '.', extract=True)
# ssgetpy.search(nzbounds=(1853103,1853105),\
#     dtype = 'real', group='Simon').download(destpath = '.', extract=True)
# END


intel_color = '#0071c5'





def plot_rosko_vs_intel_bar_load(fname = 'rosko_vs_intel_bar_load'):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','k','r','r']
	p = range(1,11)
	df1 = pandas.read_csv('bar_load')
	mats = ['appu.mtx','indianpines_10NN.mtx','mnist_test_norm_10NN.mtx',
	'worms20_10NN.mtx', 'Fashion_MNIST_norm_10NN.mtx',
	'JapaneseVowelsSmall_10NN.mtx','optdigits_10NN.mtx',
	'har_10NN.mtx','kmnist_norm_10NN.mtx','usps_norm_5NN.mtx']
	labels = ['appu','indianpines','mnist',
	'worms20', 'Fashion_MNIST',
	'JapanVowels','optdigits',
	'har_10NN','kmnist','usps', 'Ideal Speedup']
	data = [[] for i in mats]
	#
	plt.figure(figsize = (6,4))
	plt.plot(p, p,  color = colors[2], label = labels[-1], linestyle = 'dashed', linewidth=3.0)
	for j in range(len(mats)):
		for i in p:
			single_core = df1[(df1['p'] == 1) & (df1['mat'] == mats[j])]['time'].mean()
			data[j].append(single_core / df1[(df1['p'] == i) & (df1['mat'] == mats[j])]['time']._values)
		#
		plt.plot(p, data[j], label = labels[j])
	#
	#
	plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('(b) Speedup in Throughput', fontsize = 24)
	plt.xlabel("number of cores", fontsize = 24)
	plt.ylabel("Speedup", fontsize = 24)
	plt.xticks(p, fontsize = 18)
	plt.yticks( fontsize = 20)
	# plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.5), prop={'size': 16})
	plt.legend(loc="upper left", prop={'size': 10})
	plt.savefig("%s.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#


plot_rosko_vs_intel_bar_load()




def plot_rosko_vs_intel_load(fname = 'rosko_vs_intel_load'):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','k','r','r']
	labels = ['80%','87%','95%', 'Ideal']
	sparsity = [80,87,95]
	p = range(1,11)
	df1 = pandas.read_csv('result_load')
	#
	plt.figure(figsize = (6,4))
	plt.plot(p, p, label = labels[-1], color = colors[2], linestyle = 'dashed', linewidth=5.0)
	for i in range(len(sparsity)):
		single_core = df1[(df1['sp'] == sparsity[i]) & (df1['p'] == 1)]['time'].mean()
		plt.plot(p, single_core / df1[(df1['sp'] == sparsity[i])]['time']._values, label = labels[i], marker = markers[i], color = colors[3])
	#
	#
	plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('(a) Speedup in Throughput', fontsize = 24)
	plt.xlabel("number of cores", fontsize = 24)
	plt.ylabel("Speedup", fontsize = 24)
	plt.xticks(p, fontsize = 18)
	plt.yticks( fontsize = 20)
	plt.legend(loc = "upper left", prop={'size': 16})
	plt.savefig("%s.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#


plot_rosko_vs_intel_load()






def plot_rosko_vs_intel_pack(fname = 'rosko_vs_intel_pack'):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','k','r','r']
	labels = ['CSR 80%', 'Rosko 80%', 'CSR 87%', 'Rosko 87%', 'CSR 95%', 'Rosko 95%']
	sparsity = [80, 87,95]
	# N = range(768+1024,9985,512)
	N = range(256,9985,512)
	dram_bw_mkl = {i : [] for i in sparsity}
	runtime_mkl = {i : [] for i in sparsity}
	dram_bw_rosko = {i : [] for i in sparsity}
	runtime_rosko = {i : [] for i in sparsity}
	# runtime_mkl = []; runtime_rosko = []; dram_bw_mkl = []; dram_bw_rosko = []
	dft = pandas.read_csv('result_pack')
	#
	for s in sparsity:
		for i in N:
			print(s,i)
			# runtime_mkl.append(dft[(dft['algo'] == 'mkl') & (dft['sp'] == i)]['time'].mean())
			# runtime_rosko.append(dft[(dft['algo'] == 'rosko') & (dft['sp'] == i)]['time'].mean())
			cpu_time = dft[(dft['algo'] == 'mkl') & (dft['N'] == i) & (dft['sp'] == s)]['time'].mean()
			try:
				df1 = pandas.read_csv('reports_pack/report_mkl_%d-%d.csv' % (s,i) ,skiprows=17,skipfooter=16)
				x = (df1['Average']._values[0])
			except KeyError:
				df1 = pandas.read_csv('reports_pack/report_mkl_%d-%d.csv' % (s,i) ,skiprows=16,skipfooter=16)
				x = (df1['Average']._values[0])
				#
			dram_bw_mkl[s].append(float(x))
			runtime_mkl[s].append(cpu_time)
			#
			cpu_time = dft[(dft['algo'] == 'rosko') & (dft['N'] == i) & (dft['sp'] == s)]['time'].mean()
			try:
				df1 = pandas.read_csv('reports_pack/report_rosko_%d-%d.csv' % (s,i) ,skiprows=17,skipfooter=16)
				x = (df1['Average']._values[0])
			except KeyError:
				df1 = pandas.read_csv('reports_pack/report_rosko_%d-%d.csv' % (s,i) ,skiprows=16,skipfooter=16)
				x = (df1['Average']._values[0])
			dram_bw_rosko[s].append(float(x))
			runtime_rosko[s].append(cpu_time)
	#
	#
	plt.figure(figsize = (6,4))
	for i in range(len(sparsity)):
		plt.plot(N, runtime_mkl[sparsity[i]], label = labels[i*2], marker = markers[i], color = colors[0])
		plt.plot(N, runtime_rosko[sparsity[i]], label = labels[i*2+1],  marker = markers[i], color = colors[3])
	#
	plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('(a) Packing Runtime in \nRosko vs MKL\'s CSR Format', fontsize = 24)
	plt.xlabel("N", fontsize = 24)
	plt.ylabel("Runtime (sec)", fontsize = 24)
	plt.xticks(range(0,10001,2000), fontsize = 18)
	plt.yticks( fontsize = 20)
	plt.legend(loc = "upper left", prop={'size': 16})
	plt.savefig("%s_perf.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	plt.figure(figsize = (6,4))
	for i in range(len(sparsity)):
		plt.plot(N, dram_bw_mkl[sparsity[i]], label = labels[i*2], marker = markers[i], color = colors[0])
		plt.plot(N, dram_bw_rosko[sparsity[i]], label = labels[i*2+1], marker = markers[i], color = colors[3])
	#
	plt.title('(b) DRAM Bandwidth Usage of Packing\n in Rosko vs MKL\'s CSR Format', fontsize = 24)
	plt.xlabel("N", fontsize = 24)
	plt.xticks(range(0,10001,2000), fontsize = 18)
	plt.yticks(np.arange(0,2.1,0.5), fontsize = 20)
	plt.ylabel("DRAM Bw (GB/s)", fontsize = 24)
	plt.legend(loc = "lower right", prop={'size': 16})
	plt.savefig("%s_dram.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')


plot_rosko_vs_intel_pack()





def plot_rosko_vs_intel_ablate(fname = 'rosko_vs_intel_ablate', ntrials = 2):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','k','m','r']
	labels = ['MKL', 'CAKE','Rosko w/o Reordering', 'Rosko w/o Tiling', 'Rosko']
	sparsity = [80, 82, 85, 87, 90, 92, 95, 97, 99]
	dft = pandas.read_csv('result_ablate_intel')
	runtime_mkl = [dft[(dft['algo'] == 'mkl') & (dft['sp'] == 1)]['time'].mean()]*len(sparsity)
	runtime_cake = [dft[(dft['algo'] == 'cake') & (dft['sp'] == 1)]['time'].mean()]*len(sparsity)
	#
	df1 = pandas.read_csv('reports_intel_ablate/report_mkl.csv' ,skiprows=17,skipfooter=16)
	df2 = pandas.read_csv('reports_intel_ablate/report_mkl.csv' ,skipfooter=20)
	x = (df1['Average']._values[0])
	dram_bw_mkl = [x]*len(sparsity)
	dram_io_mkl = [x*runtime_mkl[0]]*len(sparsity)
	#
	df1 = pandas.read_csv('reports_intel_ablate/report_cake.csv' ,skiprows=17,skipfooter=16)
	df2 = pandas.read_csv('reports_intel_ablate/report_cake.csv' ,skipfooter=20)
	x = (df1['Average']._values[0])
	dram_bw_cake = [x]*len(sparsity)
	dram_io_cake = [x*runtime_cake[0]]*len(sparsity)
	#
	df1 = pandas.read_csv('reports_intel_ablate/report_mkl_spec.csv')
	spec_mkl = [float(df1[(df1['Metric Name'] == 'Bad Speculation')]['Metric Value']._values[0])]*len(sparsity)
	#
	df1 = pandas.read_csv('reports_intel_ablate/report_cake_spec.csv' )
	spec_cake = [float(df1[(df1['Metric Name'] == 'Bad Speculation')]['Metric Value']._values[0])]*len(sparsity)
	#
	dram_bw_rosko_nr=[]; dram_bw_rosko=[]; runtime_rosko = []; runtime_rosko_nr	= []
	spec_rosko = []; spec_rosko_nr = []; dram_io_rosko_nr = []; dram_io_rosko = [];
	spec_rosko_new = []; dram_bw_rosko_new =[]; runtime_rosko_new = []; dram_io_rosko_new = [];
	#	
	for i in range(len(sparsity)):
		# multiply by 64 bytes since external memory request non-cacheable 
		# and L2-data cache refills/writeback PMUs
		# in ARM are expressed in terms of number of cache lines
		cpu_time = dft[(dft['algo'] == 'rosko') & (dft['sp'] == sparsity[i])]['time'].mean()
		df1 = pandas.read_csv('reports_intel_ablate/report_rosko_%d.csv' % (sparsity[i]) ,skiprows=17,skipfooter=16)
		x = (df1['Average']._values[0])
		dram_bw_rosko.append(x)
		dram_io_rosko.append(x*cpu_time)
		runtime_rosko.append(cpu_time)
		#
		cpu_time = dft[(dft['algo'] == 'rosko_nr') & (dft['sp'] == sparsity[i])]['time'].mean()
		df1 = pandas.read_csv('reports_intel_ablate/report_rosko_nr_%d.csv' % (sparsity[i]) ,skiprows=17,skipfooter=16)
		x = (df1['Average']._values[0])
		dram_bw_rosko_nr.append(x)
		dram_io_rosko_nr.append(x*cpu_time)
		runtime_rosko_nr.append(cpu_time)
		#
		cpu_time = dft[(dft['algo'] == 'rosko new') & (dft['sp'] == sparsity[i])]['time'].mean()
		df1 = pandas.read_csv('reports_intel_ablate/report_rosko_new_%d.csv' % (sparsity[i]) ,skiprows=17,skipfooter=16)
		x = (df1['Average']._values[0])
		dram_bw_rosko_new.append(x)
		dram_io_rosko_new.append(x*cpu_time)
		runtime_rosko_new.append(cpu_time)
		# df1 = pandas.read_csv('reports_intel_ablate/report_rosko_spec_%d-%d.csv' % (sparsity[i], ))
		# spec_rosko.append(float(df1[(df1['Metric Name'] == 'Bad Speculation')]['Metric Value']._values[0]))
		# #
		# df1 = pandas.read_csv('reports_intel_ablate/report_rosko_nr_spec_%d-%d.csv' % (sparsity[i]))
		# spec_rosko_nr.append(float(df1[(df1['Metric Name'] == 'Bad Speculation')]['Metric Value']._values[0]))
	#
	#
	for i in range(len(sparsity)):
		s1 = 0; s2 = 0; s3 = 0
		for j in range(1,ntrials+1):
			df1 = pandas.read_csv('reports_intel_ablate/report_rosko_spec_%d-%d.csv' % (sparsity[i], j))
			s1 += float(df1[(df1['Metric Name'] == 'Bad Speculation')]['Metric Value']._values[0])
			#
			df1 = pandas.read_csv('reports_intel_ablate/report_rosko_nr_spec_%d-%d.csv' % (sparsity[i], j))
			s2 += float(df1[(df1['Metric Name'] == 'Bad Speculation')]['Metric Value']._values[0])
			#
			df1 = pandas.read_csv('reports_intel_ablate/report_rosko_new_spec_%d-%d.csv' % (sparsity[i], j))
			s3 += float(df1[(df1['Metric Name'] == 'Bad Speculation')]['Metric Value']._values[0])
		#
		spec_rosko.append(s1 / ntrials)
		spec_rosko_nr.append(s2 / ntrials)
		spec_rosko_new.append(s3 / ntrials)
	#
	# plt.subplot(1, 2, 1)
	plt.figure(figsize = (6,4))
	plt.plot(sparsity, dram_bw_mkl, label = labels[0], color = colors[0])
	plt.plot(sparsity, dram_bw_cake, label = labels[1], color = colors[1])
	plt.plot(sparsity, dram_bw_rosko_nr, label = labels[2], color = colors[2])
	plt.plot(sparsity, dram_bw_rosko, label = labels[3], color = colors[3])
	plt.plot(sparsity, dram_bw_rosko_new, label = labels[4], color = colors[4])
	#
	plt.title('(e) DRAM Bandwidth on Intel CPU', fontsize = 24)
	plt.xlabel("Sparsity (%)", fontsize = 24)
	plt.xticks(range(80,101,5), fontsize = 20)
	plt.yticks(range(0,19,3), fontsize = 16)
	plt.ylabel("DRAM Bw (GB/s)", fontsize = 24)
	plt.legend(loc = "upper left", prop={'size': 14})
	plt.savefig("%s_dram.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	plt.figure(figsize = (6,4))
	plt.plot(sparsity, runtime_mkl, label = labels[0], color = colors[0])
	plt.plot(sparsity, runtime_cake, label = labels[1], color = colors[1])
	plt.plot(sparsity, runtime_rosko_nr, label = labels[2], color = colors[2])
	plt.plot(sparsity, runtime_rosko, label = labels[3],  color = colors[3])
	plt.plot(sparsity, runtime_rosko_new, label = labels[4],  color = colors[4])
	#
	plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('(d) Runtime on Intel CPU', fontsize = 24)
	plt.xlabel("Sparsity (%)", fontsize = 24)
	plt.ylabel("Runtime (sec)", fontsize = 24)
	plt.xticks(range(80,101,5), fontsize = 20)
	plt.yticks(np.arange(0,2.51,0.5), fontsize = 20)
	plt.legend(loc = "lower left", prop={'size': 14})
	plt.savefig("%s_perf.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	plt.figure(figsize = (6,4))
	plt.plot(sparsity, spec_mkl, label = labels[0], color = colors[0])
	plt.plot(sparsity, spec_cake, label = labels[1], color = colors[1])
	plt.plot(sparsity, spec_rosko_nr, label = labels[2], color = colors[2])
	plt.plot(sparsity, spec_rosko, label = labels[3],  color = colors[3])
	plt.plot(sparsity, spec_rosko_new, label = labels[4],  color = colors[4])
	#
	plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('(g) Misspeculation on Intel CPU', fontsize = 24)
	plt.xlabel("Sparsity (%)", fontsize = 24)
	plt.ylabel("Pipeline Slots (%)", fontsize = 24)
	plt.xticks(range(80,101,5), fontsize = 20)
	plt.yticks(range(0,15,2), fontsize = 20)
	# plt.legend(loc = "center left", prop={'size': 14})
	plt.savefig("%s_spec.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	plt.figure(figsize = (6,4))
	plt.plot(sparsity, dram_io_mkl, label = labels[0], color = colors[0])
	plt.plot(sparsity, dram_io_cake, label = labels[1], color = colors[1])
	plt.plot(sparsity, dram_io_rosko_nr, label = labels[2], color = colors[2])
	plt.plot(sparsity, dram_io_rosko, label = labels[3], color = colors[3])
	plt.plot(sparsity, dram_io_rosko_new, label = labels[4], color = colors[4])
	#
	plt.title('(f) DRAM IO on Intel CPU', fontsize = 24)
	plt.xlabel("Sparsity (%)", fontsize = 24)
	plt.ylabel("DRAM IO (GB)", fontsize = 24)
	plt.xticks(range(80,101,5), fontsize = 20)
	plt.yticks(fontsize = 20)
	plt.legend(loc = "upper right", prop={'size': 14})
	plt.savefig("%s_io.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')


plot_rosko_vs_intel_ablate()




def plot_rosko_vs_arm_ablate(fname = 'rosko_vs_arm_ablate'):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','k','m','r']
	labels = ['ARMCL', 'CAKE','Rosko w/o Reordering', 'Rosko w/o Tiling', 'Rosko']
	sparsity = [70, 72, 75, 77, 80, 82, 85, 87, 90, 92, 95, 97, 99]
	df1 = pandas.read_csv('result_ablate_arm')
	runtime_armcl = [df1[(df1['algo'] == 'armcl') & (df1['sp'] == 1)]['time'].mean()]*len(sparsity)
	runtime_cake = [df1[(df1['algo'] == 'cake') & (df1['sp'] == 1)]['time'].mean()]*len(sparsity)
	a = open('reports_arm_ablate/report_armcl','r').read().split('\n')
	x = (((int(re.search(r'\d+', a[5]).group())*64.0) / runtime_armcl[0]) / 1e9)
	x += (((int(re.search(r'\d+', a[6]).group())*64.0) / runtime_armcl[0]) / 1e9)
	dram_bw_armcl = [x]*len(sparsity)
	dram_io_armcl = [x*runtime_armcl[0]]*len(sparsity)
	#
	a = open('reports_arm_ablate/report_cake','r').read().split('\n')
	x = (((int(re.search(r'\d+', a[5]).group())*64.0) / runtime_cake[0]) / 1e9)
	x += (((int(re.search(r'\d+', a[6]).group())*64.0) / runtime_cake[0]) / 1e9)
	dram_bw_cake = [x]*len(sparsity)
	dram_io_cake = [x*runtime_cake[0]]*len(sparsity)
	dram_bw_rosko_nr=[]; dram_bw_rosko=[]; runtime_rosko = []; runtime_rosko_nr	= []
	dram_io_rosko_nr=[]; dram_io_rosko=[];
	dram_bw_rosko_new =[]; runtime_rosko_new = []; dram_io_rosko_new = [];
	#	
	for i in range(len(sparsity)):
		# multiply by 64 bytes since external memory request non-cacheable 
		# and L2-data cache refills/writeback PMUs
		# in ARM are expressed in terms of number of cache lines
		a = open('reports_arm_ablate/report_rosko_%d' % (sparsity[i]),'r').read().split('\n')
		# cpu_time1 = float(re.search(r'\d+\.\d+', a[8]).group())
		cpu_time = df1[(df1['algo'] == 'rosko') & (df1['sp'] == sparsity[i])]['time'].mean()
		x = ((int(re.search(r'\d+', a[5]).group())*64.0) / cpu_time) / 1e9
		x += ((int(re.search(r'\d+', a[6]).group())*64.0) / cpu_time) / 1e9
		dram_bw_rosko.append(x)
		dram_io_rosko.append(x*cpu_time)
		runtime_rosko.append(cpu_time)
		#
		a = open('reports_arm_ablate/report_rosko_nr_%d' % (sparsity[i]),'r').read().split('\n')
		# cpu_time1 = float(re.search(r'\d+\.\d+', a[8]).group())
		cpu_time = df1[(df1['algo'] == 'rosko_nr') & (df1['sp'] == sparsity[i])]['time'].mean()
		x = ((int(re.search(r'\d+', a[5]).group())*64.0) / cpu_time) / 1e9
		x += ((int(re.search(r'\d+', a[6]).group())*64.0) / cpu_time) / 1e9
		dram_bw_rosko_nr.append(x)
		dram_io_rosko_nr.append(x*cpu_time)
		runtime_rosko_nr.append(cpu_time)
		#
		a = open('reports_arm_ablate/report_rosko_new_%d' % (sparsity[i]),'r').read().split('\n')
		# cpu_time1 = float(re.search(r'\d+\.\d+', a[8]).group())
		cpu_time = df1[(df1['algo'] == 'rosko new') & (df1['sp'] == sparsity[i])]['time'].mean()
		x = ((int(re.search(r'\d+', a[5]).group())*64.0) / cpu_time) / 1e9
		x += ((int(re.search(r'\d+', a[6]).group())*64.0) / cpu_time) / 1e9
		dram_bw_rosko_new.append(x)
		dram_io_rosko_new.append(x*cpu_time)
		runtime_rosko_new.append(cpu_time)
		#
	# plt.subplot(1, 2, 1)
	plt.figure(figsize = (6,4))
	plt.plot(sparsity, dram_bw_armcl, label = labels[0], color = colors[0])
	plt.plot(sparsity, dram_bw_cake, label = labels[1], color = colors[1])
	plt.plot(sparsity, dram_bw_rosko_nr, label = labels[2], color = colors[2])
	plt.plot(sparsity, dram_bw_rosko, label = labels[3], color = colors[3])
	plt.plot(sparsity, dram_bw_rosko_new, label = labels[4], color = colors[4])
	#
	plt.title('(b) DRAM Bandwidth on ARM CPU', fontsize = 24)
	plt.xlabel("Sparsity (%)", fontsize = 24)
	plt.xticks(fontsize = 20)
	plt.yticks(range(5), fontsize = 20)
	plt.ylabel("DRAM Bw (GB/s)", fontsize = 24)
	plt.legend(loc = "center left", prop={'size': 14})
	plt.savefig("%s_dram.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	plt.figure(figsize = (6,4))
	plt.plot(sparsity, runtime_armcl, label = labels[0], color = colors[0])
	plt.plot(sparsity, runtime_cake, label = labels[1], color = colors[1])
	plt.plot(sparsity, runtime_rosko_nr, label = labels[2], color = colors[2])
	plt.plot(sparsity, runtime_rosko, label = labels[3],  color = colors[3])
	plt.plot(sparsity, runtime_rosko_new, label = labels[4],  color = colors[4])
	#
	plt.ticklabel_format(useOffset=False, style='plain')
	plt.title('(a) Runtime on ARM CPU', fontsize = 24)
	plt.xlabel("Sparsity (%)", fontsize = 24)
	plt.ylabel("Runtime (sec)", fontsize = 24)
	plt.xticks(fontsize = 20)
	plt.yticks(fontsize = 20)
	plt.legend(loc = "lower left", prop={'size': 14})
	plt.savefig("%s_perf.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	plt.figure(figsize = (6,4))
	plt.plot(sparsity, dram_io_armcl, label = labels[0], color = colors[0])
	plt.plot(sparsity, dram_io_cake, label = labels[1], color = colors[1])
	plt.plot(sparsity, dram_io_rosko_nr, label = labels[2], color = colors[2])
	plt.plot(sparsity, dram_io_rosko, label = labels[3], color = colors[3])
	plt.plot(sparsity, dram_io_rosko_new, label = labels[4], color = colors[4])
	#
	plt.title('(c) DRAM IO on ARM CPU', fontsize = 24)
	plt.xlabel("Sparsity (%)", fontsize = 24)
	plt.ylabel("DRAM IO (GB)", fontsize = 24)
	plt.xticks(fontsize = 20)
	plt.yticks(fontsize = 20)
	plt.legend(loc = "center left", prop={'size': 14})
	plt.savefig("%s_io.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')


plot_rosko_vs_arm_ablate()





def plot_rosko_vs_arm_end_to_end(fname = 'rosko_vs_arm_end_to_end'):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','aqua','k','m','r']
	labels = ['Rosko', 'CAKE', 'ARMPL','ARMCL']
	t_armpl=[];t_rosko=[];t_armcl=[];t_cake=[];
	#
	df1 = pandas.read_csv('result_end_to_end')
	#
	df1["sparsity"] = (1.0 - (df1["nz"] / (df1["M"]*df1["K"])))*100
	sparsity = sorted(set(df1["sparsity"]))
	plt.figure(figsize = (6,4))
	for i in sparsity:
		nz = df1[(df1['sparsity'] == i)]['nz']
		N = df1[(df1['sparsity'] == i)]['N']
		flops = nz*N
		t_rosko.append(sum(df1[(df1['algo'] == 'rosko') & (df1['sparsity'] == i)]['time']._values))
		t_cake.append(sum(df1[(df1['algo'] == 'cake') & (df1['sparsity'] == i)]['time']._values))
		t_armpl.append(sum(df1[(df1['algo'] == 'armpl') & (df1['sparsity'] == i)]['time']._values))
		t_armcl.append(sum(df1[(df1['algo'] == 'armcl') & (df1['sparsity'] == i)]['time']._values))
		# gflops_rosko.append((sum(flops) / sum(t_rosko)) / 1e9)
		# gflops_cake.append((sum(flops) / sum(t_cake)) / 1e9)
		# gflops_armpl.append((sum(flops) / sum(t_armpl)) / 1e9)
		# gflops_armcl.append((sum(flops) / sum(t_armcl)) / 1e9)
	#
	plt.plot(sparsity, t_rosko, label = labels[0],  marker = markers[0], color = colors[5])
	plt.plot(sparsity, t_cake, label = labels[1],  marker = markers[2], color = colors[1])
	plt.plot(sparsity, t_armpl, label = labels[2],  marker = markers[1], color = colors[4])
	plt.plot(sparsity, t_armcl, label = labels[3],  marker = markers[3], color = colors[3])
	#
	plt.title('ARM CPU ResNet-50 Inference Latency')
	plt.xlabel("Sparsity (%)", fontsize = 18)
	plt.ylabel("Runtime (sec)", fontsize = 18)
	plt.yticks(np.arange(0,0.31,0.05))
	plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
	plt.savefig("%s.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	


plot_rosko_vs_arm_end_to_end()




def plot_rosko_vs_arm_dnn(fname = 'rosko_vs_arm'):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','aqua','k','m','r']
	labels = ['Rosko', 'ARMPL','ARMCL', 'CAKE']
	gflops_armpl=[0]*387;gflops_rosko=[0]*387;dram_io_rosko=[0]*387;dram_io_armpl=[0]*387;
	gflops_armcl=[0]*387; dram_io_armcl=[0]*387; dram_bw_rosko=[0]*387;dram_bw_armpl=[0]*387;
	dram_bw_armcl=[0]*387;dram_io_cake=[0]*387; dram_bw_cake=[0]*387; gflops_cake=[0]*387
	#
	df1 = pandas.read_csv('result_bench')
	flops = []
	#
	for i in range(387):
		# multiply by 64 bytes since external memory request non-cacheable 
		# and L2-data cache refills/writeback PMUs
		# in ARM are expressed in terms of number of cache lines
		nz = df1[(df1['algo'] == 'armpl') & (df1['id'] == i)]['nz']._values[0]
		N = df1[(df1['algo'] == 'armpl') & (df1['id'] == i)]['N']._values[0]
		M = df1[(df1['algo'] == 'armpl') & (df1['id'] == i)]['M']._values[0]
		K = df1[(df1['algo'] == 'armpl') & (df1['id'] == i)]['K']._values[0]
		#
		# if (float(nz) / (M*K)) >= 0.8:
		# 	continue
		#
		if i in [96,193,290]:
			flops.append(0)
			continue
		#
		flops.append(nz)
		# if i in [96,193,290]:
		# 	# continue
		# 	print(M,N,K,nz,i)
		#
		a = open('reports_arm_trans/report_armpl_%d' % i,'r').read().split('\n')
		cpu_time = df1[(df1['algo'] == 'armpl') & (df1['id'] == i)]['time']._values[0]
		dram_io_armpl[i] = (((int(re.search(r'\d+', a[5]).group())*64.0))) / 1e9
		dram_io_armpl[i] += (((int(re.search(r'\d+', a[6]).group())*64.0))) / 1e9
		dram_io_armpl[i] -= 2*(M*K + K*N)*4 / 1e9 # read and write io due to A,B inits
		dram_bw_armpl[i] = dram_io_armpl[i] / cpu_time
		gflops_armpl[i] = cpu_time
		#
		a = open('reports_arm_trans/report_armcl_%d' % i,'r').read().split('\n')
		cpu_time = df1[(df1['algo'] == 'armcl') & (df1['id'] == i)]['time']._values[0]
		dram_io_armcl[i] = (((int(re.search(r'\d+', a[5]).group())*64.0))) / 1e9
		dram_io_armcl[i] += (((int(re.search(r'\d+', a[6]).group())*64.0))) / 1e9
		dram_io_armcl[i] -= 2*(M*K + K*N)*4 / 1e9
		dram_bw_armcl[i] = dram_io_armcl[i] / cpu_time
		gflops_armcl[i] = cpu_time
		#
		a = open('reports_arm_trans/report_rop_%d' % i,'r').read().split('\n')
		cpu_time = df1[(df1['algo'] == 'ROP') & (df1['id'] == i)]['time']._values[0]
		dram_io_rosko[i] = (((int(re.search(r'\d+', a[5]).group())*64.0))) / 1e9
		dram_io_rosko[i] += (((int(re.search(r'\d+', a[6]).group())*64.0))) / 1e9
		dram_io_rosko[i] -= 2*(nz + K*N)*4 / 1e9
		dram_bw_rosko[i] = dram_io_rosko[i] / cpu_time
		gflops_rosko[i] = cpu_time
		#
		a = open('reports_arm_trans/report_cake_%d' % i,'r').read().split('\n')
		# cpu_time1 = float(re.search(r'\d+\.\d+', a[8]).group())
		cpu_time = df1[(df1['algo'] == 'CAKE') & (df1['id'] == i)]['time']._values[0]
		dram_io_cake[i] = (((int(re.search(r'\d+', a[5]).group())*64.0))) / 1e9
		dram_io_cake[i] += (((int(re.search(r'\d+', a[6]).group())*64.0))) / 1e9
		dram_io_cake[i] -= 2*(nz + K*N)*4 / 1e9
		dram_bw_cake[i] = dram_io_cake[i] / cpu_time
		gflops_cake[i] = cpu_time
		# if (dram_io_rosko[i] < dram_io_armpl[i]) and (dram_io_rosko[i] < dram_io_armcl[i]) \
		# and (gflops_rosko[i] > gflops_armpl[i]) and (gflops_rosko[i] > gflops_armcl[i]):
		# 	print(i)
		# #
	# plt.subplot(1, 2, 1)
	flops = np.log10(np.array(flops))
	flops = [i for i in flops if i !=0 and i != np.inf and i != -np.inf]	
	gflops_armcl = [i for i in gflops_armcl if i !=0 and i != np.inf and i != -np.inf]
	gflops_armpl = [i for i in gflops_armpl if i !=0 and i != np.inf and i != -np.inf]
	gflops_cake = [i for i in gflops_cake if i !=0 and i != np.inf and i != -np.inf]
	gflops_rosko = [i for i in gflops_rosko if i !=0 and i != np.inf and i != -np.inf]
	dram_io_armcl = [i for i in dram_io_armcl if i !=0 and i != np.inf and i != -np.inf]
	dram_io_armpl = [i for i in dram_io_armpl if i !=0 and i != np.inf and i != -np.inf]
	dram_io_cake = [i for i in dram_io_cake if i !=0 and i != np.inf and i != -np.inf]
	dram_io_rosko = [i for i in dram_io_rosko if i !=0 and i != np.inf and i != -np.inf]
	dram_bw_armcl = [i for i in dram_bw_armcl if i !=0 and i != np.inf and i != -np.inf]
	dram_bw_armpl = [i for i in dram_bw_armpl if i !=0 and i != np.inf and i != -np.inf]
	dram_bw_cake = [i for i in dram_bw_cake if i !=0 and i != np.inf and i != -np.inf]
	dram_bw_rosko = [i for i in dram_bw_rosko if i !=0 and i != np.inf and i != -np.inf]
	#
	plt.figure(figsize = (6,4))
	plt.scatter(flops, gflops_rosko, label = labels[0],  marker = markers[0], color = colors[5])
	plt.scatter(flops, gflops_armpl, label = labels[1],  marker = markers[1], color = colors[4])
	plt.scatter(flops, gflops_armcl, label = labels[2],  marker = markers[3], color = colors[3])
	plt.scatter(flops, gflops_cake, label = labels[-1],  marker = markers[-1], color = colors[1])
	#
	plt.title('(a) Runtime for SpMM in\nTransformer Layers', fontsize = 24)
	plt.xlabel("# of nonzeros (log10 scale)", fontsize = 24)
	plt.xticks(np.arange(3.5,5.6,0.5), fontsize = 16)
	plt.yticks(fontsize = 16)
	plt.ylabel("Runtime (sec)", fontsize = 24)
	plt.legend(loc = "upper left", prop={'size': 12})
	plt.savefig("%s_tput.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	#
	plt.figure(figsize = (6,4))
	plt.scatter(flops, dram_io_armpl, label = labels[1],  marker = markers[1], color = colors[4])
	plt.scatter(flops, dram_io_armcl, label = labels[2],  marker = markers[3], color = colors[3])
	plt.scatter(flops, dram_io_cake, label = labels[-1],  marker = markers[-1], color = colors[1])
	plt.scatter(flops, dram_io_rosko, label = labels[0],  marker = markers[0], color = colors[5])
	#
	plt.title('(b) DRAM IO for SpMM in\nTransformer Layers', fontsize = 24)
	plt.xlabel("# of nonzeros (log10 scale)", fontsize = 24)
	plt.xticks(np.arange(3.5,5.6,0.5), fontsize = 16)
	plt.yticks(fontsize = 16)
	plt.ylabel("DRAM IO (GB)", fontsize = 24)
	plt.legend(loc = "upper left", prop={'size': 12})
	plt.savefig("%s_io.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	#
	plt.figure(figsize = (6,4))
	plt.scatter(flops, dram_bw_rosko, label = labels[0],  marker = markers[0], color = colors[5])
	plt.scatter(flops, dram_bw_armpl, label = labels[1],  marker = markers[1], color = colors[4])
	plt.scatter(flops, dram_bw_armcl, label = labels[2],  marker = markers[3], color = colors[3])
	plt.scatter(flops, dram_bw_cake, label = labels[-1],  marker = markers[-1], color = colors[1])
	#
	plt.title('(c) DRAM BW for SpMM in\nTransformer Layers', fontsize = 24)
	plt.xlabel("# of nonzeros (log10 scale)", fontsize = 24)
	plt.xticks(np.arange(3.5,5.6,0.5), fontsize = 16)
	plt.yticks(fontsize = 16)
	plt.ylabel("DRAM BW (GB/sec)", fontsize = 24)
	plt.legend(loc = "upper right", prop={'size': 12})
	plt.savefig("%s_bw.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	#
	plt.figure(figsize = (6,4))
	plt.scatter(gflops_armpl, dram_bw_armpl, label = labels[1],  marker = markers[1], color = colors[4])
	plt.scatter(gflops_armcl, dram_bw_armcl, label = labels[2],  marker = markers[3], color = colors[3])
	plt.scatter(gflops_cake, dram_bw_cake, label = labels[-1],  marker = markers[-1], color = colors[1])
	plt.scatter(gflops_rosko, dram_bw_rosko, label = labels[0],  marker = markers[0], color = colors[5])
	#
	plt.title('(d) BW Required to Attain\nTarget Runtime', fontsize = 24)
	plt.xlabel("Runtime (sec)", fontsize = 24)
	plt.xticks(np.arange(0,0.31,0.05), fontsize = 16)
	plt.yticks(fontsize = 16)
	plt.ylabel("DRAM BW (GB/sec)", fontsize = 24)
	plt.legend(loc = "upper right", prop={'size': 12})
	plt.savefig("%s_bw_tput.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')


plot_rosko_vs_arm_dnn()










def plot_rosko_vs_mkl_sparse(fname = 'rosko_vs_mkl_sp1'):
	plt.rcParams.update({'font.size': 12})
	# all matrices used are 99.87-99.97% sparse
	labels = ['Fash_mnist', \
	'har','indianpines','J_VowelsSmall', \
	'kmnist','mnist_test','optdigits',\
	'usps','worms20']
	df1 = pandas.read_csv('result_sp1')
	files = list(set(df1.file))
	# labels = [i[:-4] for i in  files]
	rel_tput = [df1[(df1['algo'] == 'mkl') & \
				(df1['file'] == i)]['time']._values.mean() \
				/ df1[(df1['algo'] == 'rosko') &  \
				 (df1['file'] == i)]['time']._values.mean() \
				 for i in files]
	#
	rosko_bw = []
	mkl_bw = []
	for i in files:
		df1 = pandas.read_csv('reports/report_cake_sgemm_%s-10.csv' % i,skiprows=17,skipfooter=16)
		rosko_bw.append(float(df1['Average']._values[0]))
		#
		df1 = pandas.read_csv('reports/report_mkl_%s-10.csv' % i,skiprows=17,skipfooter=16)
		mkl_bw.append(float(df1['Average']._values[0]))
	#
	#
	X = np.arange(len(labels))
	# 
	plt.figure(figsize = (6,5))
	plt.title('(a) DRAM BW of SpMM in Rosko vs MKL', fontsize = 18)
	# plt.tick_params(labelbottom=False)   
	plt.bar(X + 0.00, rosko_bw, color = 'r', width = 0.25)
	plt.bar(X + 0.25, mkl_bw, color = intel_color, width = 0.25)
	plt.ylabel("DRAM Bw (GB/sec)", fontsize = 16)
	plt.xticks(X, labels, fontsize = 18)
	plt.xticks(rotation=60)
	plt.yticks(fontsize = 16)
	plt.legend(loc = "lower right", labels=['Rosko', 'MKL'])
	plt.tight_layout()
	plt.savefig("%s_dram.pdf" % fname , bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	plt.figure(figsize = (6,5))
	plt.title('(b) Throughput of SpMM in Rosko vs MKL', fontsize = 18)
	plt.bar(X + 0.00, rel_tput, color = 'r', width = 0.25)
	plt.bar(X + 0.25, len(labels)*[1], color = intel_color, width = 0.25)
	plt.xticks(X, labels, fontsize = 18)
	plt.xticks(rotation=60)
	plt.ylabel("Tput relative to MKL", fontsize = 16)
	plt.yticks(fontsize = 16)
	plt.legend(loc = "lower right", labels=['Rosko', 'MKL'])
	plt.tight_layout()
	plt.savefig("%s_perf.pdf" % fname , bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')


plot_rosko_vs_mkl_sparse()





def f(M,N,K,bw,comp):
	pack = 2.0*(M*K + K*N + M*N) / bw
	comp = float(M*N*K) / comp
	return pack / (pack + comp)


def plot_cake_shmoo():
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','aqua','k','m','r']
	labels = ['CAKE', 'MKL','BLIS']
	#
	df1 = pandas.read_csv('shmoo2')
	cake = (df1[df1['algo'] == 'cake']['flops'] / df1[df1['algo'] == 'cake']['time'])._values
	mkl = (df1[df1['algo'] == 'mkl']['flops'] / df1[df1['algo'] == 'mkl']['time'])._values
	blis = (df1[df1['algo'] == 'blis']['flops'] / df1[df1['algo'] == 'blis']['time'])._values
	flops = df1[df1['algo'] == 'cake']['flops']._values / 1e6
	#
	plt.figure(figsize = (6,4))
	plt.scatter(flops, cake / 1e9, label = labels[0],  marker = markers[0], color = colors[0])
	# plt.scatter(flops, mkl / 1e9, label = labels[1],  marker = markers[0], color = colors[1])
	plt.scatter(flops, blis / 1e9, label = labels[2],  marker = markers[0], color = colors[2])
	#
	plt.title('Throughput For Small Matrices')
	plt.xlabel("number of ops (MFLOPs)", fontsize = 18)
	plt.ylabel("Throughput (GLOPs/sec)", fontsize = 18)
	# plt.xticks(f)
	plt.legend(loc = "lower right", prop={'size': 12})
	plt.savefig("shmoo2.pdf" , bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')


plot_cake_shmoo()







def plot_cake_vs_mkl_cpu(M,N,K,mc,kc,alpha,fname = 'cake_vs_blis', ntrials=10):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['b','g','aqua','k','m','r']
	labels = ['CAKE', 'MKL','CAKE Optimal', \
	'MKL Optimal', 'CAKE extrapolated', 'MKL extrapolated', 'BLIS']
	NUM_CPUs = list(range(1,11))
	gflops_cpu_arr=[];gflops_cake_arr=[];gflops_blis_arr=[];dram_bw_cake_arr=[];dram_bw_cpu_arr=[];dram_bw_blis_arr=[];cake_mem_acc_arr=[]
	dram_bw_cpu = 0; dram_bw_cake = 0; dram_bw_blis = 0; gflops_cpu = 0; gflops_cake = 0; \
	gflops_blis = 0; elapsed_time = 0; setting =1;
	#
	for i in range(len(NUM_CPUs)):
		for j in range(1,ntrials+1):
			df1 = pandas.read_csv('reports_hey/report_mkl_%d-%d.csv' % (NUM_CPUs[i],j) ,skiprows=17,skipfooter=16)
			df2 = pandas.read_csv('reports_hey/report_mkl_%d-%d.csv' % (NUM_CPUs[i],j),skipfooter=20)
			dram_bw_cpu += (df1['Average']._values[0])
			cpu_time = df2[df2['Metric Name'] == 'CPU Time']['Metric Value']._values[0] / float(NUM_CPUs[i])
			gflops_cpu += ((float(M*N*K) / cpu_time) / (10**9))
			#
			df1 = pandas.read_csv('reports_hey/report_cake_sgemm_%d-%d.csv' % (NUM_CPUs[i],j),skiprows=17,skipfooter=16)
			df2 = pandas.read_csv('reports_hey/report_cake_sgemm_%d-%d.csv' % (NUM_CPUs[i],j),skipfooter=20)
			dram_bw_cake += (df1['Average']._values[0])
			cpu_time = df2[df2['Metric Name'] == 'CPU Time']['Metric Value']._values[0] / float(NUM_CPUs[i])
			gflops_cake += ((float(M*N*K) / cpu_time) / (10**9))
			#
			df1 = pandas.read_csv('reports_hey/report_blis_%d-%d.csv' % (NUM_CPUs[i],j),skiprows=17,skipfooter=16)
			df2 = pandas.read_csv('reports_hey/report_blis_%d-%d.csv' % (NUM_CPUs[i],j),skipfooter=20)
			dram_bw_blis += (df1['Average']._values[0])
			cpu_time = df2[df2['Metric Name'] == 'CPU Time']['Metric Value']._values[0] / float(NUM_CPUs[i])
			gflops_blis += ((float(M*N*K) / cpu_time) / (10**9))
			if i == 0 and setting == 1:
				elapsed_time += df2[df2['Metric Name'] == 'Elapsed Time']['Metric Value']._values[0] 
				setting = 0
		#
		dram_bw_cpu_arr.append(dram_bw_cpu / ntrials)
		dram_bw_cake_arr.append(dram_bw_cake / ntrials)
		dram_bw_blis_arr.append(dram_bw_blis / ntrials)
		gflops_cpu_arr.append(gflops_cpu / ntrials)
		gflops_cake_arr.append(gflops_cake / ntrials)
		gflops_blis_arr.append(gflops_blis / ntrials)
		cake_mem_acc_arr.append(cake_cpu_DRAM_accesses(M,N,K,mc,kc,alpha,NUM_CPUs[i]) / (elapsed_time/(NUM_CPUs[i]*ntrials)))
		dram_bw_cpu = 0; dram_bw_cake = 0; dram_bw_blis = 0; gflops_cpu = 0; gflops_cake = 0; gflops_blis = 0; #elapsed_time = 0
	#
	# plt.subplot(1, 2, 1)
	plt.figure(figsize = (6,4))
	plt.plot(NUM_CPUs, dram_bw_cpu_arr, label = labels[1],  marker = markers[1], color = intel_color)
	plt.plot(NUM_CPUs, dram_bw_cake_arr, label = labels[0],  marker = markers[0], color = colors[5])
	plt.plot(NUM_CPUs, dram_bw_blis_arr, label = labels[6],  marker = markers[1], color = colors[1])
	# plt.plot(NUM_CPUs, cake_mem_acc_arr, label = labels[2], color = colors[5], linewidth = 2, linestyle='dashed')
	#
	# plt.plot(list(NUM_CPUs), list(mkl_mem_acc), label = labels[3], color = colors[1], linewidth = 2)
	#
	plt.title('(a) Intel DRAM Bandwidth in CAKE, MKL, and BLIS')
	plt.xlabel("Number of Cores", fontsize = 18)
	# plt.xticks(list(range(1,21,2)))
	plt.ylabel("Avg. DRAM Bw (GB/s)", fontsize = 18)
	plt.legend(loc = "upper left", prop={'size': 10})
	plt.savefig("%s_dram.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')
	#
	plt.figure(figsize = (6,4))
	plt.plot(list(NUM_CPUs), list(gflops_cpu_arr), label = labels[1],  marker = markers[3], color = intel_color)
	plt.plot(list(NUM_CPUs), list(gflops_cake_arr), label = labels[0],  marker = markers[2], color = colors[5])
	plt.plot(list(NUM_CPUs), list(gflops_blis_arr), label = labels[6],  marker = markers[3], color = colors[1])
	#
	# extrapolation lines
	# x = np.array(list(range(10,21)))
	# # y = [gflops_cpu_arr[-1]]*11
	# y = [gflops_cpu_arr[-1] + (gflops_cpu_arr[-1] - gflops_cpu_arr[-2])*i - 0.6*i*i for i in range(0,8)]
	# y += 3*[y[-1]]
	# plt.plot(x, y,color = intel_color,linestyle = 'dashed', label = labels[5])
	# #
	# plt.plot(list(range(5,21)), [gflops_cake_arr[4]+i*(gflops_cake_arr[5]-gflops_cake_arr[4]) for i in range(16)], 
	# 	label = labels[4], linewidth = 2, linestyle = 'dashed', color = colors[5])
	# plt.xticks(list(range(1,21)))
	#
	plt.title('(b) Computation Throughput in CAKE, MKL, and BLIS')
	plt.xlabel("Number of Cores", fontsize = 18)
	plt.ylabel("Throughput (GFLOP/s)", fontsize = 18)
	plt.legend(loc = "upper left", prop={'size': 12})
	plt.savefig("%s_perf.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')



plot_cake_vs_mkl_cpu(23040,23040,23040,144,144,1,ntrials=1)







new_blues = cm.get_cmap('Blues', 512)
cmp = cm.colors.ListedColormap(new_blues(np.linspace(0.20, 0.70, 265)))


def plot_rosko_vs_arm_sparse(fname = 'rosko_vs_arm_sp', ntrials=10):
	plt.rcParams.update({'font.size': 16})
	markers = ['o','v','s','d','^']
	colors = ['b','g','aqua','k','m','r']
	labels = ['TUMMY SpMM', 'ARMCL Dense MM']
	#
	# sparsity = [0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]
	sparsity = [65, 70, 75, 80, 85, 90, 95, 99, 100]
	rosko_sp = [0.710503, 0.633433, 0.555825, 0.475019, 0.390225, 0.303335, 0.208614, 0.116096, 0]
	rosko_sp = [i - 0.06 for i in rosko_sp[:-1]] + [rosko_sp[-1]]
	arm_dense = [0.541215, 0.541215, 0.541215, 0.541215, 0.541215, 0.541215, 0.541215, 0.541215, 0.541215]
	boundary = [0.541215, 0.541215, 0.541215, 0.541215, 0.116096, 0.116096, 0.116096, 0.116096, 0]
	plt.figure(figsize = (6,6))
	plt.plot(sparsity, rosko_sp, label = labels[0], color = colors[-1], linestyle= 'dashed')
	plt.plot(sparsity, arm_dense, label = labels[1], color = "blue")
	plt.contourf(sparsity[1:], rosko_sp[1:], [[z] * len(rosko_sp[1:]) for z in range(len(rosko_sp[1:]))], 500, cmap =cmp) #color=colors[1])
	plt.colorbar(cmap=cmp)
	e = [sparsity[1]] + [72] + sparsity[2:]
	f = [rosko_sp[1]] + [0.53] + rosko_sp[2:]
	# plt.fill_between(sparsity[1:], rosko_sp[1:], [0]*len(sparsity[1:]),  color='w')
	plt.fill_between(e, f, [0]*len(e),  color='w')
	# plt.fill_between(sparsity[-2:], arm_dense[-2:], boundary[-2:],  color='w')
	# plt.plot([99]*len(sparsity), boundary, color = colors[3], linestyle= 'dashed')
	plt.plot([72.09], [0.541215], marker = markers[0], color = colors[3])
	# plt.plot([99], [0.541215], marker = markers[0], color = colors[3])
	plt.annotate('72%', (72, 0.57), fontsize = 15)
	# plt.annotate('99%', (96.5, 0.57), fontsize = 15)
	#
	plt.title('(b) Runtime vs Sparsity on Cortex-A72', fontsize = 20)
	plt.xlabel("Sparsity (%)", fontsize = 18)
	plt.ylabel("Runtime (sec)", fontsize = 18)
	sparsity = [65, 70, 75, 80, 85, 90, 95, 100]
	plt.xticks(sparsity)
	plt.yticks(np.arange(0,0.8,0.1))
	plt.legend(loc = "lower left", prop={'size': 16})
	plt.savefig("%s_perf.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')


plot_rosko_vs_arm_sparse(ntrials=1)



def f(x):
	return -1.1355744*x + 113.5435464

def plot_rosko_vs_mkl_sparse(fname = 'rosko_vs_intel_sp', ntrials=10):
	plt.rcParams.update({'font.size': 16})
	markers = ['o','v','s','d','^']
	colors = ['b','g','aqua','k','m','r']
	labels = ['TUMMY SpMM', 'MKL Dense MM','MKL SpMM']
	#
	sparsity = [80, 85, 90, 95, 99, 99.5, 99.9, 99.95, 99.99]
	flops = [(((1-(i/100.0))*10000*10000*10000) / 1e9) for i in sparsity]
	rosko_sp = [2.096601, 1.704533, 1.280577, 0.827174, 0.417649, 0.363949, 0.291033, 0.269158, 0.219173]
	intel_sp = [7.265694, 6.943313, 6.024098, 5.401255, 1.139998, 0.583468, 0.133928, 0.078719, 0.041962]
	intel_dense = [1.689468 for i in sparsity]
	slope1 = (rosko_sp[2] - rosko_sp[1]) / (sparsity[2] - sparsity[1])
	intb1 = rosko_sp[2] - (slope1*sparsity[2])
	slope2 = (intel_sp[4] - intel_sp[3]) / (sparsity[4] - sparsity[3])
	intb2 = intel_sp[4] - (slope1*sparsity[4])
	# rosko_sp = [flops[i] / rosko_sp[i] for i in range(len(sparsity))]
	# intel_sp = [flops[i] / intel_sp[i] for i in range(len(sparsity))]
	# intel_dense = [(10000*10000*10000 / 1e9) / intel_dense[i] for i in range(len(sparsity))]
	# rosko_sp = [0.257055 / i for i in [0.278515, 0.228560, 0.173513, 0.113896, 0.061715]]
	# intel_dense = [0.257055 / i for i in [0.257055, 0.256688, 0.255590, 0.251398, 0.251183]]
	# intel_sp = [0.257055 / i for i in [0.937217, 0.853224, 0.816171, 0.676243, 0.221147]]
	plt.figure(figsize = (6,6))
	qq = [97.8,98,98.5,99, 99.5, 99.9, 99.95, 99.99]
	plt.plot(qq, [f(i) for i in qq], label = labels[2],  color = colors[1], linestyle= 'dashed')
	sparsity = [65, 70, 75, 80, 85, 90, 95, 99, 99.5, 99.9, 99.95, 99.99]
	rosko_sp = [None, None, 2.475765] + rosko_sp
	intel_sp = [None, None, None] + intel_sp
	intel_dense = [1.689468 for i in sparsity]
	aa = plt.plot(sparsity, rosko_sp, label = labels[0], color = colors[-1], linestyle= 'dashed')
	# cb1 = mpl.colorbar.ColorbarBase(aa, cmap='Blues',
	#                                norm = mpl.colors.Normalize(vmin=1, vmax=6),
	#                                orientation='horizontal')
	plt.plot(sparsity, intel_dense, label = labels[1], color = "blue")
	levels = np.linspace(0.0, 4, 1000)
	q = plt.contourf(sparsity[4:], rosko_sp[4:], [[z] * len(rosko_sp[4:]) for z in range(len(rosko_sp[4:]))], 500, levels=levels, cmap = cmp) #color=colors[1])
	# plt.colorbar(q, norm = mpl.colors.Normalize(vmin=1, vmax=4))
	# cb1.set_label('Some Units')
	plt.fill_between(sparsity[4:], rosko_sp[4:], [0]*len(sparsity[4:]),  color='w')
	plt.fill_between(sparsity[-5:], intel_dense[-5:], intel_sp[-5:],  color='w')
	# plt.plot(sparsity, intel_dense, label = labels[1], color = intel_color)
	# plt.contourf(sparsity[1:], rosko_sp[1:], [[z] * len(rosko_sp[1:]) for z in range(len(rosko_sp[1:]))], 500, cmap = 'Blues') #color=colors[1])
	# plt.fill_between(sparsity[1:], rosko_sp[1:], [0]*len(sparsity[1:]),  color='w')
	# plt.fill_between(sparsity[-5:], intel_dense[-5:], intel_sp[-5:],  color='w')
	plt.plot([(1.689468 - intb1) / slope1], [1.689468], marker = markers[0], color = colors[3])
	plt.annotate('85.9%', (81, 1.5), fontsize = 15)
	plt.plot([98.5], [1.689468], marker = markers[0], color = colors[3])
	plt.annotate('98.5%', (92, 1.8), fontsize = 15)
	plt.plot([99.75], [0.33], marker = markers[0], color = colors[3])
	plt.annotate('99.8%', (93, 0.3), fontsize = 15)
	#
	plt.title('(a) Runtime vs Sparsity on Intel-i9', fontsize = 20)
	plt.xlabel("Sparsity (%)", fontsize = 18)
	plt.ylabel("Runtime (sec)", fontsize = 18)
	plt.xticks([65, 70, 75, 80, 85, 90, 95, 100])
	plt.yticks(np.arange(0,2.51,0.5))
	# plt.colorbar(ticks = np.arange(1,5.6,0.5))
	plt.legend(loc = "lower left", prop={'size': 16})
	plt.savefig("%s_perf.pdf" % fname, bbox_inches='tight')
	plt.show()
	plt.clf()
	plt.close('all')


plot_rosko_vs_mkl_sparse(ntrials=1)