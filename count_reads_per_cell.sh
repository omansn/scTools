#!/bin/sh

#warning. this script is slow and memory intensive. Not fit for large files!
bam=$1

if [[ -z "$bam" ]]; then
    echo "Must provide a bam file like: ./count_reads_per_cell.sh input.bam > output.txt" 1>&2
    exit 1
fi


samtools view $bam | grep -oP '(?<=CB:Z:)[A-T]*' | sort | uniq -c
