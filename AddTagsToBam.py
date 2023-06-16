import simplesam
import argparse

parser = argparse.ArgumentParser(
    description="Add barcode and UMI tags to bam file from list of read names, barcodes, and UMIs (tab delimeted)")
parser.add_argument('-i','--bam_in', required=True, help="input bam")
parser.add_argument('-bc','--barcode_table',required=True, help="a tab file of read names, cell barcodes")
parser.add_argument('-o','--bam_out', required=True, help="file name for tagged bam to be written")
args = parser.parse_args()

barcodes = {}
with open(args.barcode_table) as barcodes_file:
    for line in barcodes_file:
        x = line.rstrip('\t+')
        read_id, barcode = x.split()
        barcodes[read_id] = barcode
    # reading this entire file could use a TON of memory if
    # if you have lots of reads

# set the tag names - take a look at SAM spec to pick an appropriate one
barcode_tag = 'BC'

with simplesam.Reader(open(args.bam_in)) as in_bam:
    with simplesam.Writer(open(args.bam_out, 'w'), in_bam.header) as out_sam:
        for read in in_bam:
            try:
                #read[barcode_tag] = barcodes[read.qname][1]
                read[barcode_tag] = barcodes[read.qname]
                out_sam.write(read)
            except KeyError:
                read[barcode_tag] = "none"
                out_sam.write(read)
