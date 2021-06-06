#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

def getOptions():
    parser = argparse.ArgumentParser(description="Merge pairs of read counts datasets simulated for one condition")
    parser.add_argument(
        "-d1",
        "--design_c1",
        action="store",
        help="Design file name/path under which condition 1 is simulated",
    )
    parser.add_argument(
        "-d2",
        "--design_c2",
        action="store",
        help="Design file name/path under which condition 2 is simulated",
    )
    parser.add_argument(
        "-i",
        "--inputdir",
        action="store",
        help="Path to parent directory of simulated datasets",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        action="store",
        required=False,
        help="Output directory name/path. Default - $inputdir/H1_<>_H2_<>_H3_<> where <> is null or not_null",
    )
    args = parser.parse_args()
    return args


def main():
    args = getOptions()

    if "not_null" in args.design_c1:
        if "not_null" in args.design_c2: # Assumes that there is the same level of allelic imbalance for condition 1 and 2
            print("H1 not null, H2 not null, H3 null")
            if not args.outdir:
                output_dir = os.path.join(args.inputdir, "H1_not_null_H2_not_null_H3_null")
            else:
                output_dir = args.outdir
            cmd_args = [args.design_c1, "1", args.design_c2, "2", args.inputdir, output_dir]
    else:
        if "not_null" in args.design_c2:
            print("H1 null, H2 not null, H3 not null")
            if not args.outdir:
                output_dir = os.path.join(args.inputdir, "H1_null_H2_not_null_H3_not_null")
            else:
                output_dir = args.outdir
            cmd_args = [args.design_c1, "1", args.design_c2, "1", args.inputdir, output_dir]
        else:
            print("H1 null, H2 null, H3 null")
            if not args.outdir:
                output_dir = os.path.join(args.inputdir, "H1_null_H2_null_H3_null")
            else:
                output_dir = args.outdir
            cmd_args = [args.design_c1, "1", args.design_c2, "2", args.inputdir, output_dir]

    if not os.path.exists(output_dir):
         os.makedirs(output_dir)

    cmd = [sys.executable, os.path.join(sys.path[0],"tasks/merge_2_simul.py")]
    cmd.extend(cmd_args)
    print(" ".join(cmd))
    subprocess.call(cmd)


if __name__ == "__main__":
    main()
