#!/bin/python

## Given a bam file (with CB tags) and a bed file, this script will count the number of reads per cell for each bed interval. 
## This is helpful for detecting copy number changes, PCR amplification biases, and many other use cases.

import pysam
import pandas as pd
import argparse
from multiprocessing import Pool

# Function to count reads for a single interval
def count_reads_for_interval(interval):
    chrom, start, end = interval
    interval_str = str(interval).replace(', ', '-').replace('\'','')
    matrix_row = pd.Series(0, index=bc_list.barcode.values, dtype='int32')
    for read in bamfile.fetch(str(chrom), start, end, multiple_iterators=True):
        read_group = read.get_tag("CB")
        if read_group in matrix_row.index:
            matrix_row[read_group] += 1
        #print(matrix_row)
    return (interval_str, matrix_row)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Count the number of reads in a BAM file that overlap with each interval in a BED file')
parser.add_argument('--bamfile', metavar='BAM', type=str, help='the input BAM file, each read group will be a sample in the output')
parser.add_argument('--bedfile', metavar='BED', type=str, help='the input BED file')
parser.add_argument('-o', '--output', metavar='OUTPUT', type=str, default='output.csv', help='the output CSV file (default: output.csv)')
parser.add_argument('-t', '--threads', metavar='THREADS', type=int, default=1, help='the number of processing threads to use (default: 1)')
parser.add_argument('-b', '--barcodes', metavar="BARCODES", type = str, help = 'the barcode file')
args = parser.parse_args()

# Open BC list
bc_list = pd.read_csv(args.barcodes, names = ["barcode"], sep = '\t')
# Open BAM file and get read groups
bamfile = pysam.AlignmentFile(args.bamfile, "rb")
#read_groups = [rg['ID'] for rg in bamfile.header['RG']]

# Open BED file and read intervals
bedfile = pd.read_csv(bed_path, sep="\t", header=None, skiprows = 1)
#bed_intervals = bedfile.iloc[:, 0:3].apply(lambda row: (row[0], row[1], row[2]), axis=1)
bed_intervals = bedfile.iloc[:, 0:3].apply(lambda row: (row[0].replace("chr", ""), int(row[1]), int(row[2])), axis=1)
# Initialize matrix with zeros
matrix = pd.DataFrame(0, index=[str(interval).replace(', ', '-').replace('\'','') for interval in bed_intervals], columns=bc_list.barcode.values)

# Create a pool of worker processes
pool = Pool(args.threads)

# Map the intervals to worker processes and collect results
try:
    results = pool.map(count_reads_for_interval, bed_intervals)
except KeyError:
    pass

# Combine results into the matrix
for interval_str, matrix_row in results:
    matrix.loc[interval_str, :] = matrix_row


#rgf = '\t'.join(map(str,read_groups))
#matrix.columns = read_groups
# Write output to file
matrix.to_csv(args.output, index_label='chrom,start,end')
