#!/usr/bin/env python3

import argparse
import os
import pandas as pd
import numpy as np

def getOptions():
    parser = argparse.ArgumentParser(description="Summarize the posterior estimates after fitting NB model to data")
    parser.add_argument(
        "-o",
        "--outfile",
        action="store",
        required=False,
        help="Output file name/path. Default - posterior_estimates_summary_across_simul.csv",
    )
    parser.add_argument(
        "-i",
        "--inputdirs",
        action="store",
        nargs='*',
        help="(List of) folder(s) with outputs from Bayesian ASE model to summarize",
    )
    args = parser.parse_args()
    return args


def compute_prop_hypothesis(dir_list):
    """Function to summarize results of analysis of data with Bayesian model
         Arguments:
           :param dir_list: A list of directories from which to read files
           :type datadir: list
         Returns:
           :return : Dataframe with simulation parameters and summary statistics of model posterior estimates
           :rypte: Pandas DataFrame
    """
    array_all_estimate = np.empty((0,38), dtype=float)
    for dir in dir_list:
        for filename in os.listdir(dir):
            if len(list(filter(filename.endswith, ['r_out', 'temp']))) == 0:
                print(filename)
                df_result = pd.read_csv(os.path.join(dir, filename), sep="\t")
                scenario = df_result['comparison'][0].split('_')
                scenario = {name:value for name,value in zip(scenario[::2], scenario[1::2])}
                coverage_per_biorep = int(scenario['allelicreads'])/2/int(scenario['nbiorep'])/np.mean([float(scenario['rsim-g1']), float(scenario['rsim-g2'])]) ## This includes the reads that map best to an allele g1 (or g2) and
                                                                                                                                        ## equally well to both alleles given it was generated by g1 (or g2)
                num_allele_specific_reads_per_biorep = float(scenario['allelicreads'])/int(scenario['nbiorep'])
                alpha1_sim = np.sqrt((1/float(scenario['theta1']))-1) ## In the stan2 model, theta = 1/(alpha[i]^2+1)
                alpha2_sim = np.sqrt((1/float(scenario['theta2']))-1)
                delta_ai_1 = round(abs(float(scenario['theta1'])-0.5)/0.5, 2) ## |theta1 - theta0| / theta0 where theta0 = 0.5
                delta_ai_2 = round(abs(float(scenario['theta2'])-0.5)/0.5, 2) ## |theta2 - theta0| / theta0 where theta0 = 0.5
                delta_ai_3 = round(abs(float(scenario['theta2'])-float(scenario['theta1']))/float(scenario['theta1']), 2) ## |theta2 - theta1| / theta1
                nfeature = df_result.shape[0]
                alpha1_avg = np.mean(df_result['alpha1_postmean'])
                alpha1_median = np.median(df_result['alpha1_postmean'])
                alpha1_variance = np.var(df_result['alpha1_postmean'])
                alpha2_avg = np.mean(df_result['alpha2_postmean'])
                alpha2_median = np.median(df_result['alpha2_postmean'])
                alpha2_variance = np.var(df_result['alpha2_postmean'])
                theta1_avg = np.mean(df_result['c1_theta'])
                theta1_median = np.median(df_result['c1_theta'])
                theta1_variance = np.var(df_result['c1_theta'])
                theta2_avg = np.mean(df_result['c2_theta'])
                theta2_median = np.median(df_result['c2_theta'])
                theta2_variance = np.var(df_result['c2_theta'])
                c1_sampleprop_avg = np.mean(df_result['c1_sampleprop'])
                c1_sampleprop_median = np.median(df_result['c1_sampleprop'])
                c1_sampleprop_variance = np.var(df_result['c1_sampleprop'])
                c2_sampleprop_avg = np.mean(df_result['c2_sampleprop'])
                c2_sampleprop_median = np.median(df_result['c2_sampleprop'])
                c2_sampleprop_variance = np.var(df_result['c2_sampleprop'])
                prop_H1_LE05 = sum(df_result['c1_Bayes_evidence']<0.05)/nfeature
                prop_H1_LE01 = sum(df_result['c1_Bayes_evidence']<0.01)/nfeature
                prop_H2_LE05 = sum(df_result['c2_Bayes_evidence']<0.05)/nfeature
                prop_H2_LE01 = sum(df_result['c2_Bayes_evidence']<0.01)/nfeature
                prop_H3_LE05 = sum(df_result['H3_independence_Bayes_evidence']<0.05)/nfeature
                prop_H3_LE01 = sum(df_result['H3_independence_Bayes_evidence']<0.01)/nfeature
                array_all_estimate = np.append(array_all_estimate, np.array([[nfeature, scenario['rsim-g1'], scenario['rsim-g2'], 
                                            int(scenario['nbiorep']), num_allele_specific_reads_per_biorep, scenario['allelicreads'], coverage_per_biorep, 
                                            scenario['theta1'], scenario['theta2'], delta_ai_1, delta_ai_2, delta_ai_3, alpha1_sim, alpha2_sim,
                                            alpha1_avg, alpha1_median, alpha1_variance, alpha2_avg, alpha2_median, alpha2_variance, theta1_avg,
                                            theta1_median, theta1_variance, theta2_avg, theta2_median, theta2_variance, c1_sampleprop_avg,
                                            c1_sampleprop_median, c1_sampleprop_variance, c2_sampleprop_avg, c2_sampleprop_median,
                                            c2_sampleprop_variance, prop_H1_LE05, prop_H1_LE01, prop_H2_LE05, prop_H2_LE01, prop_H3_LE05, prop_H3_LE01]]), axis=0)

    column_names = ['nfeature', 'r_g1', 'r_g2', 'num_bioreps', 'num_allele_specific_reads_per_biorep', 'num_allele_specific_reads', 'coverage_per_biorep', 
                    'theta1_sim', 'theta2_sim', 'delta_AI_1', 'delta_AI_2', 'delta_AI_3',
                    'alpha1_sim', 'alpha2_sim', 
                    'average_alpha1', 'median_alpha1', 'variance_alpha1', 'average_alpha2', 'median_alpha2', 'variance_alpha2',
                    'average_theta1', 'median_theta1', 'variance_theta1', 'average_theta2', 'median_theta2', 'variance_theta2',
                    'average_c1_sampleprop', 'median_c1_sampleprop', 'variance_c1_sampleprop',
                    'average_c2_sampleprop', 'median_c2_sampleprop', 'variance_c2_sampleprop',
                    'prop_H1_LE05', 'prop_H1_LE01', 'prop_H2_LE05', 'prop_H2_LE01', 'prop_H3_LE05', 'prop_H3_LE01']

    return(pd.DataFrame(array_all_estimate, columns=column_names))


def main():
    args = getOptions()
    df_result = compute_prop_hypothesis(args.inputdirs)
    if not args.outfile:
        outfile = "posterior_estimates_summary_across_simul.csv"
    else:
        outfile = args.outfile

    df_result.to_csv(outfile, index=False)


if __name__ == "__main__":
    main()