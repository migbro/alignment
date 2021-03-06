#!/usr/bin/env python3
"""
Usage: ./fastq_file <fastq>

Options:
-h

Arguments:
<fastq> fastq file

"""
import gzip
import os
import sys

from Bio import SeqIO

from docopt import docopt

args = docopt(__doc__)
fn = args['<fastq>']
fastq = gzip.open(fn, 'rt')
sys.stderr.write('Processing file ' + fn + '\n')
indir = os.path.dirname(fn)
bn = os.path.basename(fn)
if not os.path.isdir(indir + '/converted'):
    os.mkdir(indir + '/converted')
out = gzip.open(indir + '/converted/' + bn, 'wt')
sys.stderr.write('Opened output file ' + indir + '/converted/' + bn + '\n')
# code snippets obtained from https://github.com/vpiro/readtools/blob/master/PHRED_converter.py
quali = 'fastq-illumina'
qualo = 'fastq-sanger'
sys.stderr.write('Converting file\n')
SeqIO.convert(fastq, quali, out, qualo)
fastq.close()
out.close()
sys.stderr.write('Finished!\n')
