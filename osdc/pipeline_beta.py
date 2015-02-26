#!/usr/bin/python
# written by Miguel Brown 2015-Feb-11. test run based on align.pl calls just to confirm successful installation of tools on pipeline vm

import sys
sys.path.append('/home/ubuntu/TOOLS/Scripts/modules')
import os
import re
import argparse
from date_time import date_time
from fastx import fastx
from bwa_mem_pe import bwa_mem_pe
from picard_sort_pe import picard_sort_pe
from picard_rmdup import picard_rmdup
from picard_insert_size import picard_insert_size
from flagstats import flagstats
import coverage
from subprocess import call

parser=argparse.ArgumentParser(description='DNA alignment paired-end QC pipeline')
parser.add_argument('-f1','--file1',action='store',dest='end1',help='First fastq file')
parser.add_argument('-f2','--file2',action='store',dest='end2',help='Second fastq file')
parser.add_argument('-t','--seqtype',action='store',dest='seqtype',help='Type of sequencing peformed.  Likely choices are genome, exome, and target for capture')
if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

inputs=parser.parse_args()

end1=inputs.end1
end2=inputs.end2
seqtype=inputs.seqtype
sys.stderr.write(date_time() + "Starting alignment qc for paired end sample files " + end1 + " and " + end2 + "\n")
#inputs

SAMPLES={}

s=re.match('^(\S+)_1_sequence\.txt\.gz$',end1)

sample=s.group(1)
HGACID=sample.split("_")
SAMPLES[sample]={}
SAMPLES[sample]['f1']=end1
SAMPLES[sample]['f2']=end2
RGRP="@RG\\tID:" + sample + "\\tLB:" + HGACID[0] + "\\tSM:" + HGACID[0] + "\\tPL:illumina"

#tools and refs

log_dir='LOGS/'
mk_log_dir='mkdir ' + log_dir
sys.stderr.write(date_time() + 'Made log directory ' + log_dir + "\n")
call(mk_log_dir,shell=True)

ref_mnt="REFS_" + HGACID[0]
fastx_tool='fastx_quality_stats'
bwa_tool='/home/ubuntu/TOOLS/bwa-0.7.8/bwa'
bwa_ref='/mnt/cinder/' + ref_mnt + '/REFS/bwa-0.7.8/hg19.fa'
samtools_tool='/home/ubuntu/TOOLS/samtools-0.1.19/samtools'
samtools_ref='/mnt/cinder/' + ref_mnt + '/REFS/samtools-0.1.19/hg19.fa'
java_tool='/home/ubuntu/TOOLS/jdk1.7.0_45/bin/java'
picard_tool='/home/ubuntu/TOOLS/picard/dist/picard.jar'
picard_tmp='picard_tmp'
bedtools2_tool='/home/ubuntu/TOOLS/bedtools2/bin/bedtools'
#reference for coverage set by seqtype
bed_ref={}
bed_ref['exome']='/mnt/cinder/' + ref_mnt + '/REFS/BED/refseq.Hs19.coding_regions.merged.bed'
bed_ref['genome']='/mnt/cinder/' + ref_mnt + '/REFS/BED/hg19_complete_sorted.bed'
bed_ref['target']='/mnt/cinder/' + ref_mnt + '/REFS/BED/capture_panel_2.0.bed'
parse_qc_stats='/home/ubuntu/TOOLS/Scripts/parse_qc_stats.pl'

wait_flag=1

#fastx(fastx_tool,sample,end1,end2) # will run independently of rest of output
#bwa_mem_pe(bwa_tool,RGRP,bwa_ref,end1,end2,samtools_tool,samtools_ref,sample,log_dir) # rest won't run until completed
#picard_sort_pe(java_tool,picard_tool,picard_tmp,sample,log_dir) # rest won't run until completed
#picard_rmdup(java_tool,picard_tool,picard_tmp,sample,log_dir)  # rest won't run until emopleted
#flagstats(samtools_tool,sample) # flag determines whether to run independently or hold up the rest of the pipe until completion

#picard_insert_size(java_tool,picard_tool,sample,log_dir) # get insert size metrics. 
#figure out which coverage method to call using seqtype
method=getattr(coverage,(seqtype+'_coverage'))
#method(bedtools2_tool,sample,bed_ref[seqtype],wait_flag) # run last since this step slowest of the last

# check to see if last expected file was generated search for seqtype + .hist suffix
flist=os.listdir('./')
f=0
suffix=seqtype+'.hist'
for fn in flist:
    if fn==(sample +'.' + suffix):
        f=1
        break
if f==1:
    from upload_to_swift import upload_to_swift
    upload_to_swift(HGACID[0],sample)
    sys.stderr.write(date_time() + "Pipeline process completed!\n")
else:
    sys.stderr.write(date_time() + "File with suffix " + suffix + " is missing!  If intentional, ignore this message.  Otherwise, check logs for potential failures\n")
    exit(3)