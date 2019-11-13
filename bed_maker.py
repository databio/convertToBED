#!/usr/bin/env python

from argparse import ArgumentParser
import pypiper
import os
import sys

parser = ArgumentParser(description = "A pipeline to convert bigwig or bedgraph files into bed format")


parser.add_argument("-f", "--input-file", help="path to the input file", type=str)
parser.add_argument("-c", "--chip-exp", help="is it a ChIP-Seq TF experiment or a Histone modification ChiP-Seq experiment", type=bool)
parser.add_argument("-t", "--input-type", help="a bigwig or a bedgraph file that will be converted into BED format")
parser.add_argument("-o", "--outfolder", default="output", help="folder to put the converted BED files in")


# add pypiper args to make pipeline looper compatible
parser = pypiper.add_pypiper_args(parser, groups=["pypiper", "looper"],
                                            required=["--input-file", "--input-type", "--chip-exp", "--outfolder"])

args = parser.parse_args()

# COMMANDS TEMPLATES

# bedGraph to bed
bedGraph_template = "macs2 {width} -i {input} -o {output}"
# bigBed to bed
bigBed_template = "bigBedToBed {input} {output}"
# preliminary bigWig to bed
bigWig_template = "bigWigToBedGraph {input} /dev/stdout | macs2 {width} -i /dev/stdin -o {output}"


def get_bed_path(current_path, outfolder):
    """
    Swap the file extension and change the directory

    :param str current_path: current path to the file to be converted
    :param str outfolder: output directory to place the file with the swapped extension in
    :return str: path to the file with swapped extension
    """
    file_name = os.path.basename(current_path)
    file_id = os.path.splitext(file_name)[0]
    return os.path.join(outfolder, file_id + ".bed")


def main():
    pm = pypiper.PipelineManager(name="bed_maker", outfolder=args.outfolder, args=args) #args defined with ArgParser and add_pypiper_args

    # Define target folder for converted files and implement the conversions; True=TF_Chipseq False=Histone_Chipseq
    target = get_bed_path(args.input_file, args.outfolder)

    print("Got input type: {}".format(args.input_type))
    print("Converting {} to BED format".format(args.input_file))

    width = "bdgbroadcall" if not args.chip_exp else "bdgpeakcall"

    # if args.chip_exp:
    if args.input_type == "bedGraph":
        cmd = bedGraph_template.format(input=args.input_file, output=target, width=width)
    elif args.input_type == "bigWig":
        cmd = bigWig_template.format(input=args.input_file, output=target, width=width)
    elif args.input_type == "bigBed":
        cmd = bigBed_template.format(input=args.input_file, output=target)
    else:
        raise NotImplementedError("Other conversions are not supported")

    pm.run(cmd, target=target)
    pm.stop_pipeline()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("Pipeline aborted.")
        sys.exit(1)
