#!/usr/bin/python
import sys

sys.path.append('/home/ubuntu/TOOLS/Scripts/utility')
from date_time import date_time
import subprocess
import json


def parse_config(config_file):
    config_data = json.loads(open(config_file, 'r').read())
    return config_data['tools']['VEP'], config_data['refs']['vepCache'], config_data['refs']['fa_ordered'],\
           config_data['params']['threads'], config_data['tools']['snpsift'], config_data['tools']['java'], \
           config_data['refs']['cadd']


def pass_filter(sample):
    in_fn = sample + '.germline_calls.vcf'
    out_fn = sample + '.germline_pass.vcf'
    out = open(out_fn, 'w')
    infile = open(in_fn, 'r')
    for line in infile:
        if line[0] == '#':
            out.write(line)
        else:
            fields = line.split('\t')
            if fields[6] == 'PASS':
                out.write(line)
    infile.close()
    out.close()


def annot_platypus(config_file, samp_list, ref_mnt):
    (vep_tool, vep_cache, fasta, threads, snpsift, java, cadd) = parse_config(config_file)
    fasta = ref_mnt + '/' + fasta
    cadd = ref_mnt + '/' + cadd
    vep_cache = ref_mnt + '/' + vep_cache
    # scale back on the forking a bit
    if int(threads) > 2:
        threads = str(int(threads) - 1)
    # parse sample file, use only last if pairs
    samp_fh = open(samp_list, 'r')
    for line in samp_fh:
        info = line.rstrip('\n').split('\t')
        sample = info[0]
        if len(info) > 1:
            sample = info[3]
        pass_filter(sample)
        mk_log_dir = 'mkdir LOGS'
        subprocess.call(mk_log_dir, shell=True)
        run_vep = 'perl ' + vep_tool + ' --cache -i ' + sample + '.germline_pass.vcf --vcf -o ' + sample\
                  + '.germline_pass.vep.vcf --symbol --vcf_info_field ANN --canonical --html --variant_class --sift b --offline --maf_exac' \
                    ' --no_whole_genome --fork ' + threads + ' --fasta ' + fasta + ' --dir_cache ' + vep_cache\
                  + ' --plugin CADD,' + cadd + ' 2>> LOGS/' + sample + '.vep.log;'
        check = subprocess.call(run_vep, shell=True)
        if check == 0:
            sys.stderr.write(date_time() + 'SNP annotation of germline calls completed!\n')
        else:
            sys.stderr.write(date_time() + 'SNP annotation of germline calls for ' + sample + ' FAILED!\n')
            return 1
        # #field_list = ('CHROM', 'POS', 'REF', 'ALT', 'TR' 'SYMBOL', )
        # table_cmd = java + ' -jar ' + snpsift + ' extractFields ' + sample + '.germline_pass.vep.vcf CHROM POS REF ALT TR TC'\
        #         '"ANN[0].Consequence" "ANN[0].SYMBOL" "ANN[0].BIOTYPE" "ANN[0].SIFT" "ANN[0].Amino_acids" ' \
        #         '"ANN[0].ExAC_MAF" "ANN[0].ExAC_Adj_MAF" "ANN[0].CLIN_SIG" "ANN[0].PHENO" "ANN[0].CADD_PHRED" "ANN[0].CADD_RAW" > ' + sample + '.germline_pass.xls'
        # sys.stderr.write(table_cmd + '\n')
        # check = subprocess.call(table_cmd, shell=True)
        # if check == 0:
        #    sys.stderr.write(date_time() + 'Germline table for ' + sample + ' created!\n')
        #    return 0
        # else:
        #    sys.stderr.write(date_time() + 'Germline table for ' + sample + ' failed!\n')

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='SNP annotation.')
    parser.add_argument('-j', '--json', action='store', dest='config_file',
                        help='JSON config file with tool and reference locations')
    parser.add_argument('-sp', '--sample_pairs', action='store', dest='sample_pairs', help='Sample tumor/normal pairs')
    parser.add_argument('-r', '--ref_mnt', action='store', dest='ref_mnt',
                        help='Reference mount directory, i.e. /mnt/cinder/REFS_XXX')


    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    inputs = parser.parse_args()
    (config_file, sample_pairs, ref_mnt) = (
        inputs.config_file, inputs.sample_pairs, inputs.ref_mnt)
    annot_platypus(config_file, sample_pairs, ref_mnt)