#!/usr/bin/env python3

import sys
sys.path.append('/cephfs/users/mbrown/PIPELINES/DNAseq/')
from utility.date_time import date_time
from utility.job_manager import job_manager
import subprocess
import json


def parse_config(config_file):
    config_data = json.loads(open(config_file, 'r').read())
    return (config_data['tools']['java'], config_data['tools']['gatk'], config_data['refs']['genome'],
            config_data['refs']['fa_ordered'], config_data['params']['threads'], config_data['params']['ram'])


def mutect_pipe(config_file, sample_pairs, ref_mnt):
    (java, gatk, intervals, fa_ordered, max_t, ram) = parse_config(config_file)
    intervals = ref_mnt + '/' + intervals
    # break up intervals into max threads junks to run all in parallel
    int_fh = open(intervals, 'r')
    int_dict = {}
    i = 0
    # create temp directory
    tmp_cmd = 'mkdir temp'
    subprocess.call(tmp_cmd, shell=True)
    # create sub-interval files - split by chromosome
    mk_dir_bed = 'mkdir bed'
    subprocess.call(mk_dir_bed, shell=True)
    for interval in int_fh:
        (chrom, start, end) = interval.split('\t')
        intvl = start + '-' + end  # normally not need if using normal interval file
        try:
            int_dict[chrom]['fh'].write(interval)
        except:
            int_dict[chrom] = {}
            int_dict[chrom]['fn'] = 'bed/intervals_' + chrom + '.bed'
            int_dict[chrom]['fh'] = open(int_dict[chrom]['fn'], 'w')
            int_dict[chrom]['fh'].write(interval)
        i += 1
    fa_ordered = ref_mnt + '/' + fa_ordered
    fh = open(sample_pairs)
    job_ram = (int(ram) / int(max_t))
    run_mut = java + ' -Djava.io.tmpdir=./temp -Xmx' + str(job_ram) + 'g -jar ' + gatk
    mk_log_dir = 'mkdir LOGS'
    subprocess.call(mk_log_dir, shell=True)
    for line in fh:
        # array will store commands to run, next def will take care of job management using popen
        cmd_list = []
        line = line.rstrip('\n')
        (sample, tumor_id, normal_id) = line.split('\t')
        tumor_bam = tumor_id + '.merged.final.bam'
        normal_bam = normal_id + '.merged.final.bam'
        sys.stderr.write(date_time() + 'Processing pair T: ' + tumor_bam + ' N: ' + normal_bam + '\n')
        out = tumor_id + '_' + normal_id
        # make result directory for current pair
        mk_res = 'mkdir ' + out
        subprocess.call(mk_res, shell=True)
        i = 1
        for intvl in sorted(int_dict):
            int_dict[intvl]['fh'].close()
            cur = run_mut
            vcf_file = out + '.' + intvl + '.vcf'
            log_file = 'LOGS/' + out + '.mut.' + intvl + '.log'
            cur = cur + ' -T MuTect2 -S LENIENT -R ' + fa_ordered + ' --intervals ' + int_dict[intvl]['fn'] + \
                  '  -I:normal ' + normal_bam + '  -I:tumor ' + tumor_bam + ' --max_alt_alleles_in_normal_count 1000'\
                  ' --max_alt_alleles_in_normal_qscore_sum 37 --max_alt_allele_in_normal_fraction 0.05 --out ' + out \
                  + '/' + vcf_file + ' 2>> ' + log_file + ';'
            cmd_list.append(cur)
            i += 1
        # fix encode flag won't work if alread phred 33, if a job fails try without
        try:
            job_manager(cmd_list, max_t)
        except:
            for i in range(0, len(cmd_list), 1):
                cmd_list[i] = cmd_list[i].replace('-fixMisencodedQuals ', '')
            job_manager(cmd_list, max_t)
    sys.stderr.write(date_time() + 'Variant calling completed!\n')
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='muTect2 pipleine for variant calling.  Need BAM and bai files ahead of time.')
    parser.add_argument('-j', '--json', action='store', dest='config_file',
                        help='JSON config file with tool and reference locations')
    parser.add_argument('-sp', '--sample_pairs', action='store', dest='sample_pairs', help='Sample tumor/normal pairs')
    parser.add_argument('-r', '--ref_mnt', action='store', dest='ref_mnt',
                        help='Reference drive path - i.e. /mnt/cinder/REFS_XXXX')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    inputs = parser.parse_args()
    (config_file, sample_pairs, ref_mnt) = (inputs.config_file, inputs.sample_pairs, inputs.ref_mnt)
    mutect_pipe(config_file, sample_pairs, ref_mnt)
