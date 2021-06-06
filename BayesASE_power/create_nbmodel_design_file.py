#!/usr/bin/env python3

import argparse
import os

def getOptions():
    parser = argparse.ArgumentParser(description="Fit Bayesian model to read count data")
    parser.add_argument(
        "-i",
        "--infile",
        action="store",
        help="Filename of simulated read count dataset",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        action="store",
        required=False,
        help="Output design file name/path. Default - condition_design_file.tsv in current working directory",
    )
    args = parser.parse_args()
    return args


def main():
    args = getOptions()
    input_filename = os.path.splitext(os.path.basename(args.infile))[0]

    if not args.outfile:
        outfile = "condition_design_file.tsv"
    else:
        outfile = args.outfile

    with open(outfile, "w") as output:
        output.write('\t'.join(["Comparate_1", "Comparate_2", "compID"]) + "\n")
        output.write('\t'.join(["c1", "c2", input_filename]))


if __name__ == "__main__":
    main()