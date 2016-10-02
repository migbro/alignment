#!/usr/bin/python
import sys

sys.path.append('/home/ubuntu/TOOLS/Scripts/utility')
from date_time import date_time
import subprocess
import json


def parse_config(config_file):
    config_data = json.loads(open(config_file, 'r').read())
    return (config_data['tools']['java'], config_data['tools']['snpEff'], config_data['tools']['snpsift'],
            config_data['refs']['dbsnp'], config_data['refs']['intervals'])

def pass_filter(sample):
    in_fn = sample + '/somatic.indel.vcf'
    out_fn = sample + '/' + sample + 'somatic.indel.PASS.vcf'
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

def annot_scalpel(config_file, sample, ref_mnt):
    (java, snpeff, snpsift, dbsnp, intervals) = parse_config(config_file)
    pass_filter(sample)
    out_fn = sample + '/' + sample + 'somatic.indel.PASS.vcf'
    out_fn1 = sample + '/' + sample + 'somatic.indel.PASS.sift.vcf'
    out_fn2 = sample + '/' + sample + 'somatic.indel.PASS.eff.vcf'
    dbsnp = ref_mnt + '/' + dbsnp
    mk_log_dir = 'mkdir LOGS'
    subprocess.call(mk_log_dir, shell=True)
    run_snpsift = java + ' -jar ' + snpsift + ' annotate ' + dbsnp
    run_snpeff = java + ' -jar ' + snpeff + ' eff -t hg19 '
    run_snp = run_snpsift + ' ' + out_fn + ' > ' + out_fn1 + ' 2> LOGS/'\
              + sample + '.snpeff.log;' + run_snpeff + ' ' + out_fn1 + ' -v > ' + out_fn2 \
              + ' 2>> LOGS/' + sample + '.snpeff.log;'
    check = subprocess.call(run_snp, shell=True)
    if check == 0:
        sys.stderr.write(date_time() + 'SNP annotation of indel calls completed!\n')
    else:
        sys.stderr.write(date_time() + 'SNP annotation of indel calls for ' + sample + ' FAILED!\n')
        return 1

    #table_cmd = java + ' -jar ' + snpsift + ' extractFields ' + sample + '.germline_pass.eff.vcf CHROM POS ID REF ALT '\
    #            '"EFF[0].EFFECT" "EFF[0].CODON" "EFF[0].AA" "EFF[0].AA_LEN" "EFF[0].GENE" ' \
    #            '"EFF[0].BIOTYPE" "EFF[0].CODING" > ' + sample + '.germline_pass.xls'
    #check = subprocess.call(table_cmd, shell=True)
    #if check == 0:
    #    sys.stderr.write(date_time() + 'Germline table created!\n')
    #    return 0
    #else:
    #    sys.stderr.write(date_time() + 'Germline table failed!\n')
    return 0

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
    annot_scalpel(config_file, sample_pairs, ref_mnt)