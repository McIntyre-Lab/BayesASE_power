#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import pandas as pd

#try:
#    from importlib import resources as ires
#except ImportError:
#    import importlib_resources as ires

def getOptions():
    parser = argparse.ArgumentParser(description="Simulated RNA-seq read counts")
    parser.add_argument(
        "-d",
        "--design",
        action="store",
        help="CSV design file with simulation parameters",
    )
    parser.add_argument(
        "-s",
        "--sets",
        action="store",
        type=int,
        default=2,
        help="Optional number of sets of simulations to do with the parameters (default: 2)",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        action="store",
        help="Path to directory where to save output",
    )
    args = parser.parse_args()
    return args


def main():
    args = getOptions()

    r_script = os.path.join(sys.path[0], "tasks/simulate_read_counts_NBmodel.r")
    # Once the package is built with set up files, i think this is what you want:
    #with ires.path("BayesASE_power", "simulate_read_counts_NBmodel_05kos.r") as R_path:
    #        r_script = str(R_path)

    df = pd.read_csv(args.design, dtype=str)

    # iterate over design file
    for index, row in df.iterrows():

        for i in range(args.sets):

            if float(row["theta"]) == 0.5:
                if not os.path.exists(os.path.join(args.outdir, "H1_null")):
                    os.makedirs(os.path.join(args.outdir, "H1_null"))
                routput = os.path.join(args.outdir, "H1_null", "out_set_"+str(i+1))
            else:
                if not os.path.exists(os.path.join(args.outdir, "H1_not_null")):
                    os.makedirs(os.path.join(args.outdir, "H1_not_null"))
                routput = os.path.join(args.outdir, "H1_not_null", "out_set_"+str(i+1))

            cmd = [
                    "Rscript",
                    r_script,
                    row["theta"],
                    row["simruns"],
                    routput,
                    row["nbiorep"],
                    row["n_allele_specific_reads"]
                    ]
            print(" ".join(cmd))

            subprocess.call(cmd)


if __name__ == "__main__":
    main()

