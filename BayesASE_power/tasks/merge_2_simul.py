#1/bin/usr/env python3

import argparse
import pandas as pd
import os
import ntpath

parser = argparse.ArgumentParser()
parser.add_argument('simul1', help='CSV design file for setting up simulations for first comparate')
parser.add_argument('simul1_set', help='Which set of simulations and value of theta for first comparate to consider')
parser.add_argument('simul2', help='CSV design file for setting up simulations for second comparate')
parser.add_argument('simul2_set', help='Which set of simulations and value of theta for second comparate to consider')
parser.add_argument('simuldir', help='Parent directory of simulated datasets')
parser.add_argument('outdir', help='Directory to which to output merged data')
args = parser.parse_args()

def create_filelist(design_file, set_num):
    filelist = []
    with open(design_file, 'r') as design:
        for index, line in enumerate(design):
            if index == 0:
                header = line.strip().split(',')
            else:
                param = line.strip().split(',')
                scenario = {header[i]:param[i] for i in range(len(header))}
                print(scenario)
                try:
                    r_g1 = scenario['rsim-g1']
                    r_g2 = scenario['rsim-g2']
                except KeyError:
                    r_g1 = r_g2 = 0.8

                filelist.append('out_set_'+set_num+'_theta_'+scenario['theta']+'_rsim-g1_'+str(r_g1)+'_rsim-g2_'+ \
                                str(r_g2)+'_nbiorep_'+scenario['nbiorep']+'_allelicreads_'+ \
                                scenario['n_allele_specific_reads']+'_simruns_'+scenario['simruns']+'.tsv')
    return(filelist)

df_c1_files = pd.DataFrame(create_filelist(args.simul1, args.simul1_set), columns = ['c1'])
df_c1_files['c1'] = ntpath.basename(args.simul1).split("design_")[1].split("_null")[0]+"_null"+'/'+df_c1_files['c1'].astype(str)
df_c2_files = pd.DataFrame(create_filelist(args.simul2, args.simul2_set), columns = ['c2'])
df_c2_files['c2'] = ntpath.basename(args.simul2).split("design_")[1].split("_null")[0]+"_null"+'/'+df_c2_files['c2'].astype(str)

if 'not_null' in os.path.basename(args.simul1) and 'not_null' in os.path.basename(args.simul2):
    df_c1_param = df_c1_files['c1'].str.split('_theta', 1, expand=True)
    df_c1_files['param'] = 'theta'+df_c1_param[1].astype(str)
    df_c1_files['c1_theta'] = df_c1_param[1].str.split('_rsim', expand=True)[0]
    df_c1_files['c1_theta'] = 'theta1'+df_c1_files['c1_theta'].astype(str)

    df_c2_param = df_c2_files['c2'].str.split('_theta', 1, expand=True)
    df_c2_files['param'] = 'theta'+df_c2_param[1].astype(str)
    df_c2_files['c2_theta'] = df_c2_param[1].str.split('_rsim', expand=True)[0]
    df_c2_files['c2_theta'] = 'theta2'+df_c2_files['c2_theta'].astype(str)
else:
    df_c1_param = df_c1_files['c1'].str.split('_rsim', 1, expand=True)
    df_c1_files['c1_theta'] = df_c1_param[0].str.split('theta', expand=True)[1].str.replace('_', 'theta1_')
    df_c1_files['param'] =  df_c1_param[1]

    df_c2_param = df_c2_files['c2'].str.split('_rsim', 1, expand=True)
    df_c2_files['c2_theta'] = df_c2_param[0].str.split('theta', expand=True)[1].str.replace('_', 'theta2_')
    df_c2_files['param'] =  df_c2_param[1]

df_both_comparates = pd.merge(df_c1_files, df_c2_files, on='param', how='inner')
print(df_both_comparates)

for index, row in df_both_comparates.iterrows():
    print(args.simuldir)
    print(row['c1'])
    df_c1_simul = pd.read_csv(os.path.join(args.simuldir, row['c1']), sep="\t")
    df_c2_simul = pd.read_csv(os.path.join(args.simuldir, row['c2']), sep="\t")
    df_c2_simul.drop(['FEATURE_ID'], axis=1, inplace=True)
    df_c2_simul.columns = df_c2_simul.columns.str.replace('c1', 'c2')
    if 'H1_not_null_H2_not_null_H3_null' in args.outdir:
        filename = row['c1_theta'] + '_' + row['c2_theta'] + '_'+row['param'].split('_', 2)[-1]
    else:
        filename = row['c1_theta'] + '_' + row['c2_theta'] + '_rsim'+row['param']
    print(filename)
    pd.concat([df_c1_simul, df_c2_simul], axis=1, sort=False).to_csv(os.path.join(args.simuldir, args.outdir, filename), index=False, sep="\t") 
