#!/usr/bin/env python3

import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
import seaborn as sns ### To import colorblind color palette

def getOptions():
    parser = argparse.ArgumentParser(description="Plot Type I error and power")
    parser.add_argument(
        "-p",
        "--param",
        action="store",
        # default="all",
        help="One of the simulated parameters for which to produce plots: 'nfeature', 'num_allele_specific_reads_per_biorep', 'delta_AI', 'num_bioreps",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        action="store",
        required=False,
        help="Full path to directory to store plots. Default - ./data_visualization",
    )
    parser.add_argument(
        "-i",
        "--infile",
        action="store",
        nargs='*',
        help="(List of) CSV file(s)/path(s) of parameters used for simulation and summary statistics of Bayesian model posterior estimates",
    )
    args = parser.parse_args()
    return(args)

def specify_data_to_plot(df_data, xaxis, hypothesis, legend, flag_power, delta_AI = None):
    """Function to create a dataframe of the data that is to be plotted
         Arguments:
           :param df_data: Subset of the data to be plotted
           :type datadir: Pandas DataFrame

           :param xaxis: Name of simulation parameter that is plotted on x axis
           :type datadir: string

           :param hypothesis: Either "H1" for evaluation of one condition or "H3" for comparison between two conditions
           :type datadir: string

           :param legend: Name of the simulation parameter for which each line is drawn in the plot. Specifies plot legend.
           :type datadir: string

           :param flag_power: "1" if the plot y axis is power or "0" if it is Type I error 
           :type flag_power: int (0 or 1)

           :param delta_AI: If not None, only consider rows of the dataframe with delta_AI_1, _2, and _3 that are that value
           :type delta_AI: float

         Returns:
           :return : Dataframe with data in format necessary to use the create_plot function
           :rypte: Pandas DataFrame
    """
    df_data_w_legend = pd.DataFrame()
    for index, row in df_data.iterrows():
        if flag_power == 1:
            if hypothesis == "H1":
                if delta_AI:
                    if row.delta_AI_1 == delta_AI:
                        df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row[xaxis], "prop_LE05":row.prop_H1_LE05, legend: row[legend]}]))
                    if row.delta_AI_2 == delta_AI:
                            df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row[xaxis], "prop_LE05":row.prop_H2_LE05, legend: row[legend]}]))
                else:
                    if row.delta_AI_1 != 0:
                        df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row[xaxis], "prop_LE05":row.prop_H1_LE05, legend: row[legend]}]))
                    if row.delta_AI_2 != 0:
                        if legend == "delta_AI_1":
                            df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row[xaxis], "prop_LE05":row.prop_H2_LE05, legend: row.delta_AI_2}]))
                        if xaxis == "delta_AI_1":
                            df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row["delta_AI_2"], "prop_LE05":row.prop_H2_LE05, legend: row[legend]}]))
            if hypothesis == "H3":
                if delta_AI: 
                    if row.delta_AI_3 == delta_AI:
                        df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row[xaxis], "prop_LE05":row.prop_H3_LE05, legend: row[legend]}]))
                else:
                    if row.delta_AI_3 != 0:
                        df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row[xaxis], "prop_LE05":row.prop_H3_LE05, legend: row[legend]}]))
        else:
            if hypothesis == "H1":
                if row.delta_AI_1 == 0:
                    df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row[xaxis], "prop_LE05":row.prop_H1_LE05, legend: row[legend]}]))
                if row.delta_AI_2 == 0:
                    df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row[xaxis], "prop_LE05":row.prop_H2_LE05, legend: row[legend]}]))
            if hypothesis == "H3":
                if row.delta_AI_3 == 0:
                    df_data_w_legend = df_data_w_legend.append(pd.DataFrame([{xaxis:row[xaxis], "prop_LE05":row.prop_H3_LE05, legend: row[legend]}]))
    return(df_data_w_legend)

def create_plot(df_data_w_legend, hypothesis, colormap, flag_power_plot, ax=None, title=None):
    """Function to create subplots for type I error or power in rejecting H1(/H2) and H3
         Arguments:
           :param df_data_w_legend: dataframe with x axis values in 1st column, 
                y axis values in 2nd column, and simulation parameter to use in legend in 3rd column
           :type datadir: Pandas DataFrame

           :param hypothesis: Either "H1" for evaluation of one condition or "H3" for comparison 
                between two conditions
           :type datadir: string

           :param colormap: Specify what should be the color of the line drawn for each one of the 
                simulation parameter values in legend
           :type datadir: dictionary

           :param flag_power_plot: "1" if the plot y axis is power or "0" if it is Type I error 
           :type flag_power_plot: int (0 or 1)

           :param ax: If not None, axes on which to draw plot
           :type ax: AxesSubplot

           :param title: If not None, title of subplot. Only used when xaxis is number of bioreps.
           :type title: string

         Returns:
           :return: subplot
           :rypte: AxesSubplot
    """
    map_colname_to_plt_label = {"nfeature": "Number of Simulations", "num_allele_specific_reads": "# of Allele Specific Reads", 
                                "num_allele_specific_reads_per_biorep": "# of Allele Specific Reads Per Biorep",
                                "delta_AI_1": r"$\Delta$$AI_1$", "delta_AI_3": r"$\Delta$$AI_3$", "num_bioreps": "Number of Bioreps"}
    if ax is None: ax = plt.gca()
    for grp, df_grp in df_data_w_legend.groupby(df_data_w_legend.columns[2]):
        # print(grp)
        # print(df_grp)
        df_xaxis_grp = df_grp.groupby(df_grp.columns[0]).agg({"prop_LE05": ["mean", "sem"]})
        if df_xaxis_grp["prop_LE05"]["sem"].isnull().all():
            if hypothesis == "H1":
                df_xaxis_grp["prop_LE05"]["mean"].plot(ax=ax, marker=".", linestyle = "-", color=colormap[grp],  
                                                label=hypothesis+", "+map_colname_to_plt_label[df_data_w_legend.columns[2]]+"="+str(grp)).legend(loc="center right", bbox_to_anchor=(-0.13, 0.5))
            else:
                df_xaxis_grp["prop_LE05"]["mean"].plot(ax=ax, marker=".", linestyle = "--", color=colormap[grp],  
                                                label=hypothesis+", "+map_colname_to_plt_label[df_data_w_legend.columns[2]]+"="+str(grp)).legend(loc="center left", bbox_to_anchor=(1.0, 0.5))
        else:
            if hypothesis == "H1":
                df_xaxis_grp["prop_LE05"]["mean"].plot(yerr=df_xaxis_grp["prop_LE05"]["sem"], ax=ax, marker=".", linestyle = "-", color=colormap[grp],  
                                                label=hypothesis+", "+map_colname_to_plt_label[df_data_w_legend.columns[2]]+"="+str(grp)).legend(loc="center right", bbox_to_anchor=(-0.13, 0.5))
                                                #legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2)
            else:
                df_xaxis_grp["prop_LE05"]["mean"].plot(yerr=df_xaxis_grp["prop_LE05"]["sem"], ax=ax, marker=".", linestyle = "--", color=colormap[grp],  
                                                label=hypothesis+", "+map_colname_to_plt_label[df_data_w_legend.columns[2]]+"="+str(grp)).legend(loc="center left", bbox_to_anchor=(1.0, 0.5))
                                                #legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2)
        ax.set_ylim([0, 1.05]) if flag_power_plot == 1 else ax.set_ylim([0, 0.1])
        if df_data_w_legend.columns[0] == "nfeature":
            ax.set_xlim([min(df_data_w_legend[df_data_w_legend.columns[0]])-250, max(df_data_w_legend[df_data_w_legend.columns[0]])+250])
            ax.xaxis.set_major_locator(MultipleLocator(500))
        elif df_data_w_legend.columns[0] == "num_allele_specific_reads_per_biorep":
            ax.set_xlim([min(df_data_w_legend[df_data_w_legend.columns[0]])-50, max(df_data_w_legend[df_data_w_legend.columns[0]])+50]) 
            ax.xaxis.set_major_locator(MultipleLocator(50))
            ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
            ax.xaxis.set_minor_locator(MultipleLocator(10))
        elif df_data_w_legend.columns[0] == "num_bioreps":
            ax.set_xlim([min(df_data_w_legend[df_data_w_legend.columns[0]])-1, max(df_data_w_legend[df_data_w_legend.columns[0]])+1]) 
            ax.xaxis.set_major_locator(MultipleLocator(1))
            ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        else:
            ax.set_xlim([min(df_data_w_legend[df_data_w_legend.columns[0]])-0.05, max(df_data_w_legend[df_data_w_legend.columns[0]])+0.05]) 
            ax.xaxis.set_major_locator(MultipleLocator(0.1))
        ax.tick_params(labelrotation=45)
        ax.set_ylabel("Power") if flag_power_plot == 1 else ax.set_ylabel("Type I Error")
        ax.set_xlabel(map_colname_to_plt_label[df_data_w_legend.columns[0]])
        if title: ax.title.set_text(title) 
    return(ax)


def setup(param, df_data, t1er_param, power_param, fixed_param, legend_param, color_palette, output, delta_AI=None):
    """Function to setup the parameters needed to run the functions that subset the data for 
        plotting and create the plots
         Arguments:
           :param param: Assess the type I error and power as affected by this simulation parameter
           :type param: string

           :param df_data: Dataframe summarizing parameters used to create simualted data and
                summary statistics of model parameters estimates.
           :type df_data: string

           :param t1er_param: Simulation parameter that is plotted on x axiis of the type I error plots
           :type t1er_param: string

           :param power_param: Simulation parameter that is plotted on x axiis of the power plots
           :type power_param: string

           :param fixed_param: Simulation parameter(s) that are fixed when creating the plots
           :type fixed_param: string or list

           :param legend_param: Simulation parameter corresponding to the values in the legend for which
                a line in the plot is created
           :type legend_param: string

           :param color_palette: Specify what should be the color of the line drawn for each one of the 
                simulation parameter values in legend
           :type color_palette: dictionary

           :param output: Directory to which to save plots
           :type output: string

           :param delta_AI: If not None, value of delta_AI_1 (delta_AI_2) and delta_AI_3 that should be kept 
                constant when creating plots of type I error or power in rejecting H1 (H2) or H3, respectively.
           :type delta_AI: float
    """
   
    for group, df_group in df_data.groupby(fixed_param, sort=False):
        print(str(fixed_param)+": "+str(group))
        # print(df_group.iloc[:, 0:9])
        if (delta_AI is None) or (delta_AI == 0):
            if isinstance(legend_param, dict):
                H1_legend_param = legend_param["t1er"]["H1"]
                H3_legend_param = legend_param["t1er"]["H3"]
            else:
                H1_legend_param = H3_legend_param = legend_param
            df_H1_t1er = specify_data_to_plot(df_group, t1er_param["H1"], "H1", H1_legend_param, 0)
            df_H3_t1er = specify_data_to_plot(df_group, t1er_param["H3"], "H3", H3_legend_param, 0)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13,5))
            if param == "num_bioreps":
                if not df_H1_t1er.empty: create_plot(df_H1_t1er, "H1", color_palette, 0, ax1, r"$\Delta$$AI_1$=0")
                if not df_H3_t1er.empty: create_plot(df_H3_t1er, "H3", color_palette, 0, ax2, r"$\Delta$$AI_3$=0")
                filename = ["t1er_BE_LE05_vs", param, fixed_param, str(group), "legend_is", legend_param, "delta_AI", str(0)]
            else:
                if not df_H1_t1er.empty: create_plot(df_H1_t1er, "H1", color_palette, 0, ax1)
                if not df_H3_t1er.empty: create_plot(df_H3_t1er, "H3", color_palette, 0, ax2)
                filename = ["t1er_BE_LE05_vs", param, fixed_param[0], str(group[0]), fixed_param[1], str(group[1])]
            if (df_H1_t1er.empty==False) or (df_H3_t1er.empty==False):
                plt.savefig(os.path.join(output, "_".join(filename)+".jpg"), bbox_inches = "tight", dpi=100)
                plt.close(fig)
        if (delta_AI is None) or (delta_AI > 0):
            if isinstance(legend_param, dict):
                H1_legend_param = legend_param["power"]["H1"]
                H3_legend_param = legend_param["power"]["H3"]
            else:
                H1_legend_param = H3_legend_param = legend_param
            df_H1_power = specify_data_to_plot(df_group, power_param["H1"], "H1", H1_legend_param, 1, delta_AI)
            df_H3_power = specify_data_to_plot(df_group, power_param["H3"], "H3", H3_legend_param, 1, delta_AI)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13,5))
            if param == "num_bioreps":
                filename = ["power_BE_LE05_vs", param, fixed_param, str(group), "legend_is", legend_param, "delta_AI", str(delta_AI)]
                if not df_H1_power.empty: create_plot(df_H1_power, "H1", color_palette, 1, ax1, r"$\Delta$$AI_1$="+str(delta_AI))
                if not df_H3_power.empty: create_plot(df_H3_power, "H3", color_palette, 1, ax2, r"$\Delta$$AI_3$="+str(delta_AI))
            else:
                filename = ["power_BE_LE05_vs", param, fixed_param[0], str(group[0]), fixed_param[1], str(group[1])]
                if not df_H1_power.empty: create_plot(df_H1_power, "H1", color_palette, 1, ax1)
                if not df_H3_power.empty: create_plot(df_H3_power, "H3", color_palette, 1, ax2)
            if (df_H1_power.empty==False) or (df_H3_power.empty==False):
                plt.savefig(os.path.join(output, "_".join(filename)+".jpg"), bbox_inches = "tight", dpi=100)
                plt.close(fig)


def main():
    args = getOptions()
    outdir = args.outdir if args.outdir else os.path.join(os.path.curdir, "data_visualization")
    if not os.path.exists(outdir): os.makedirs(outdir)
    df_summary = pd.read_csv(args.infile[0])
    if len(args.infile) > 1:
        for infile in args.infile[1:]:
            df_infile = pd.read_csv(infile)
            df_summary = pd.concat([df_summary, df_infile])
    # print(df_summary)
    df_summary.reset_index(drop=True, inplace=True)

    t1er_xaxis_param = {"H1": "delta_AI_3", "H3": "delta_AI_1"} if args.param == "delta_AI" else {"H1": args.param, "H3": args.param}
    power_xaxis_param = {"H1": "delta_AI_1", "H3": "delta_AI_3"} if args.param == "delta_AI" else {"H1": args.param, "H3": args.param}
    if args.param == "delta_AI":
        fixed = ["num_bioreps", "nfeature"]
        legend_values = sorted(set(df_summary["num_allele_specific_reads"]))
        colors = dict(zip(legend_values , sns.color_palette("colorblind", len(legend_values))))
        setup(args.param, df_summary, t1er_xaxis_param, power_xaxis_param, fixed, "num_allele_specific_reads", colors, outdir)
    elif args.param == "num_bioreps":
        fixed = "nfeature"
        all_delta_AI = sorted((set(df_summary["delta_AI_1"]).union(set(df_summary["delta_AI_2"])).union(set(df_summary["delta_AI_3"]))))
        colors = {}
        legend_values = sorted(set(df_summary["num_allele_specific_reads"]))
        colors["num_allele_specific_reads"] = dict(zip(legend_values , sns.color_palette("colorblind", len(legend_values))))
        legend_values = sorted(set(df_summary["num_allele_specific_reads_per_biorep"]))
        colors["num_allele_specific_reads_per_biorep"] = dict(zip(legend_values , sns.color_palette("colorblind", len(legend_values))))
        for legend_param in colors.keys():
            for delta in [d for d in all_delta_AI]: 
                setup(args.param, df_summary, t1er_xaxis_param, power_xaxis_param, fixed, legend_param, colors[legend_param], outdir, delta)
    else: 
        fixed = ["num_bioreps", "num_allele_specific_reads"] ### if args.param == "num_features" 
        if args.param == "num_allele_specific_reads_per_biorep": fixed = ["nfeature", "num_bioreps"]
        legend_param = {"t1er": {"H1": "delta_AI_3", "H3": "delta_AI_1"}, "power": {"H1": "delta_AI_1", "H3": "delta_AI_3"}}
        legend_values = sorted((set(df_summary["delta_AI_1"]).union(set(df_summary["delta_AI_2"])).union(set(df_summary["delta_AI_3"]))))
        colors = dict(zip(legend_values , sns.color_palette("colorblind", len(legend_values))))
        setup(args.param, df_summary, t1er_xaxis_param, power_xaxis_param, fixed, legend_param, colors, outdir)


if __name__ == "__main__":
    main()
