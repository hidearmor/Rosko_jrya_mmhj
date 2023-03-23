import pandas
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cm as cm
import numpy as np
import os
import re
import sys
from matplotlib import ticker as mticker
from scipy import stats
from scipy.stats import gmean



def plot_rosko_gnn(fname = 'rosko_gnn'):
	plt.rcParams.update({'font.size': 12})
	markers = ['o','v','s','d','^']
	colors = ['r', 'b', 'g', 'k','g','m']
	labels = ['Rosko','FeatGraph', 'MKL_CSR']
	barWidth = 0.15
	#
	df1 = pandas.read_csv('result_gnn')
	feat_lens = [32, 64, 128, 256, 512]
	speedup1 = []
	speedup2 = []
	#
	#
	for file in ['reddit', 'ogbn']:
		#
		feat_time=[];opt=[];dram_bw_rosko=[];dram_bw_feat=[];dram_bw_mkl=[]
		rosko_time = df1[(df1['algo'] == 'rosko') & (df1['file'] == '%s_packed' % file)]['time'].values
		M = df1[(df1['algo'] == 'rosko') & (df1['file'] == '%s_packed' % file)]['M'].values
		K = df1[(df1['algo'] == 'rosko') & (df1['file'] == '%s_packed' % file)]['K'].values
		flops = (1.0 - df1[(df1['algo'] == 'rosko') & (df1['file'] == '%s_packed' % file)]['sp'].values / 100.0)*M*K*np.array(feat_lens) / 1e9
		rosko_flops = flops / rosko_time
		#
		mkl_time = df1[(df1['algo'] == 'mkl') & (df1['file'] == '%s_packed' % file)]['time'].values
		M = df1[(df1['algo'] == 'mkl') & (df1['file'] == '%s_packed' % file)]['M'].values
		K = df1[(df1['algo'] == 'mkl') & (df1['file'] == '%s_packed' % file)]['K'].values
		flops = (1.0 - df1[(df1['algo'] == 'mkl') & (df1['file'] == '%s_packed' % file)]['sp'].values / 100.0)*M*K*np.array(feat_lens) / 1e9
		mkl_flops = flops / mkl_time
		#
		for j in range(len(feat_lens)):
			a = open('feat_%s_%d' % (file,feat_lens[j]),'r').read()
			feat_time.append(min(map(float,re.findall(r'\d+\.\d+',a))))
			col_part = []
			feat_part = []
			feat1 = []
			q = a.split('\n')
			x = [q[i:i+4] for i in range(0,len(q),4)]
			x = [i for i in x if i != ['']]
			for i in x:
				col_part.append(int(re.findall(r'\d+',i[1])[0]))
				feat_part.append(int(re.findall(r'\d+',i[2])[0]))
				feat1.append(float(re.findall(r'\d+\.\d+',i[3])[0]))
			#
			opt.append(min(zip(col_part, feat_part, feat1), key = lambda t: t[2]))
			#
			#
			#
			df2 = pandas.read_csv('reports_gnn/report_rosko_%s_%d.csv' % (file,feat_lens[j]) ,skiprows=17,skipfooter=16)
			dram_bw = df2['Average']._values[0]
			df2 = pandas.read_csv('reports_gnn/report_rosko_%s_%d.csv' % (file,feat_lens[j]),skipfooter=20)
			elapsed = df2[df2['Metric Name'] == 'Elapsed Time']['Metric Value']._values[0]
			#
			df3 = pandas.read_csv('reports_gnn/report_rosko_%s_setup_%d.csv' % (file,feat_lens[j]) ,skiprows=17,skipfooter=16)
			dram_bw1 = df3['Average']._values[0]
			df3 = pandas.read_csv('reports_gnn/report_rosko_%s_setup_%d.csv' % (file,feat_lens[j]),skipfooter=20)
			elapsed1 = df3[df3['Metric Name'] == 'Elapsed Time']['Metric Value']._values[0]
			dram_bw = ((dram_bw*elapsed) - (dram_bw1*elapsed1)) / (elapsed-elapsed1)
			dram_bw_rosko.append(dram_bw)
			#
			#
			df2 = pandas.read_csv('reports_gnn/report_feat_%s_%d.csv' % (file,feat_lens[j]) ,skiprows=17,skipfooter=16)
			dram_bw = df2['Average']._values[0]
			df2 = pandas.read_csv('reports_gnn/report_feat_%s_%d.csv' % (file,feat_lens[j]),skipfooter=20)
			elapsed = df2[df2['Metric Name'] == 'Elapsed Time']['Metric Value']._values[0]
			#
			df3 = pandas.read_csv('reports_gnn/report_feat_%s_setup_%d.csv' % (file,feat_lens[j]) ,skiprows=17,skipfooter=16)
			dram_bw1 = df3['Average']._values[0]
			df3 = pandas.read_csv('reports_gnn/report_feat_%s_setup_%d.csv' % (file,feat_lens[j]),skipfooter=20)
			elapsed1 = df3[df3['Metric Name'] == 'Elapsed Time']['Metric Value']._values[0]
			dram_bw = ((dram_bw*elapsed) - (dram_bw1*elapsed1)) / (elapsed-elapsed1)
			dram_bw_feat.append(dram_bw)
			#
			#
			try:
				df2 = pandas.read_csv('reports_gnn/report_mkl_%s_%d.csv' % (file,feat_lens[j]) ,skiprows=16,skipfooter=16)
				dram_bw = df2['Average']._values[0]
			except KeyError:
				df2 = pandas.read_csv('reports_gnn/report_mkl_%s_%d.csv' % (file,feat_lens[j]) ,skiprows=17,skipfooter=16)
				dram_bw = df2['Average']._values[0]
			df2 = pandas.read_csv('reports_gnn/report_mkl_%s_%d.csv' % (file,feat_lens[j]),skipfooter=20)
			elapsed = df2[df2['Metric Name'] == 'Elapsed Time']['Metric Value']._values[0]
			#
			try:
				df3 = pandas.read_csv('reports_gnn/report_mkl_%s_setup_%d.csv' % (file,feat_lens[j]) ,skiprows=17,skipfooter=16)
				dram_bw1 = float(df3['Average']._values[0])
			except KeyError:
				df3 = pandas.read_csv('reports_gnn/report_mkl_%s_setup_%d.csv' % (file,feat_lens[j]) ,skiprows=16,skipfooter=16)
				dram_bw1 = float(df3['Average']._values[0])
			df3 = pandas.read_csv('reports_gnn/report_mkl_%s_setup_%d.csv' % (file,feat_lens[j]),skipfooter=22)
			elapsed1 = df3[df3['Metric Name'] == 'Elapsed Time']['Metric Value']._values[0]
			dram_bw = ((dram_bw*elapsed) - (dram_bw1*elapsed1)) / (elapsed-elapsed1)
			dram_bw_mkl.append(dram_bw)
			#
			#
		feat_flops = flops / np.array(feat_time)
		plt.figure(figsize = (6,4))
		plt.title('GNN SpMM Throughput\non %s Dataset' % file.capitalize(), fontsize = 20)
		# plt.plot(feat_lens, rosko_flops_reddit, color ='r', label = labels[0])
		# plt.plot(feat_lens, feat_flops_reddit, color ='m', label =labels[1])
		br1 = np.arange(len(feat_lens))
		br2 = [x + barWidth for x in br1]
		br3 = [x + barWidth for x in br2]
		plt.bar(br1, rosko_flops, color ='r', width = barWidth,
		        edgecolor ='grey', label = labels[0])
		plt.bar(br2, feat_flops, color ='m', width = barWidth,
		        edgecolor ='grey', label =labels[1])
		plt.bar(br3, mkl_flops, color ='b', width = barWidth,
		        edgecolor ='grey', label =labels[2])
		plt.xlabel("Feature Length", fontsize = 20)
		# plt.xticks(feat_lens)
		plt.xticks([r + barWidth for r in range(len(feat_lens))],
	        feat_lens, fontsize = 14)
		plt.yticks(fontsize = 16)
		plt.ylabel("Throughput (GFLOPs/sec)", fontsize = 20)
		if file == 'reddit':
			plt.legend(loc = "upper right", prop={'size': 12})
		else:
			plt.legend(loc = "lower left", prop={'size': 12})			
		plt.savefig("%s_%s_tput.pdf" % (file,fname), bbox_inches='tight')
		plt.show()
		plt.clf()
		plt.close('all')
		#
		#
		plt.figure(figsize = (6,4))
		plt.title('GNN SpMM DRAM Bandwidth\non %s Dataset' % file.capitalize(), fontsize = 20)
		# plt.plot(feat_lens, rosko_flops_reddit, color ='r', label = labels[0])
		# plt.plot(feat_lens, feat_flops_reddit, color ='m', label =labels[1])
		br1 = np.arange(len(feat_lens))
		br2 = [x + barWidth for x in br1]
		br3 = [x + barWidth for x in br2]
		plt.bar(br1, dram_bw_rosko, color ='r', width = barWidth,
		        edgecolor ='grey', label = labels[0])
		plt.bar(br2, dram_bw_feat, color ='m', width = barWidth,
		        edgecolor ='grey', label =labels[1])
		plt.bar(br3, dram_bw_mkl, color ='b', width = barWidth,
		        edgecolor ='grey', label =labels[2])
		plt.xlabel("Feature Length", fontsize = 20)
		# plt.xticks(feat_lens)
		plt.xticks([r + barWidth for r in range(len(feat_lens))],
	        feat_lens, fontsize = 14)
		plt.yticks(fontsize = 16)
		plt.ylabel("Dram BW (GB/sec)", fontsize = 20)
		if file == 'reddit':
			plt.legend(loc = "upper right", prop={'size': 12})
		else:
			plt.legend(loc = "lower left", prop={'size': 12})			
		# plt.savefig("%s.pdf" % fname, bbox_inches='tight')
		plt.show()
		plt.clf()
		plt.close('all')
		speedup1 += list(np.array(rosko_flops) / np.array(mkl_flops))
		speedup2 += list(np.array(rosko_flops) / np.array(feat_flops))
		#
		print("speedup over mkl = %f" %  gmean(speedup1))
		print(stats.describe(speedup1))
		print("speedup over featgraph = %f" % gmean(speedup2))
		print(stats.describe(speedup2))



plot_rosko_gnn()





