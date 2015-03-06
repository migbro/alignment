#!/usr/bin/python
import sys
from date_time import date_time
import subprocess
import os
import re

def fq2lane(fq_list,seqtype):
    fh=open(fq_list,'r')
    cur={}
    for line in fh:
        line=line.rstrip('\n')
        f1=re.match('^(\d+-\d+)_(\S+)_\d+_sequence.txt.gz$',line)
        line=next(fh)
        bid=f1.group(1)
        lane=f1.group(2)
        if bid not in cur:
            cur[bid]=[]
        cur[bid].append(lane)
    for bid in cur:
        sys.stdout.write(bid + '\t' + seqtype + '\t')
        lane=", ".join(cur[bid])
        sys.stdout.write(lane + '\n')
        
if __name__ == "__main__":
    import argparse

    parser=argparse.ArgumentParser(description='Simple tool to convert a fastq list to input that pipeline_wrapper would accept')
    parser.add_argument('-f','-fastq_list',action='store',dest='fq_list',help='Fastq file listing')
    parser.add_argument('-s','--seqtype',action='store',dest='seqtype',help='Seqtype, i.e. genome, capture')
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    inputs=parser.parse_args()
    fq_list=inputs.fq_list
    seqtype=inputs.seqtype

    fq2lane(fq_list,seqtype)