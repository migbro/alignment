import sys
from date_time import date_time
import subprocess
import os
import re

def attach_cinder(sid,vid,bid,size,vip,wait):
    cname = "REFS_" + bid
    sys.stderr.write(date_time() + "Creating cinder volume " + cname + " using snapshot ID " + sid + "to vm with ID " + vid + "\n")
    # need build variables to call nova successfully
    src_cmd='. /home/ubuntu/.novarc;'
    vol_cmd=src_cmd+"cinder create " + size + " --snapshot-id " + sid + " --display_name " + cname
    subprocess.call(vol_cmd, shell=True)
    
    # check status of vm until finshed spawing every 30s                                                                                                                         
    i=30
    sleep='sleep ' + str(i) + 's'
    n=i
    flag=0
    cid=''
    while flag==0:
        subprocess.call(sleep, shell=True)
        if n > wait:
            break
        else:
            sys.stderr.write(date_time() + "Checking success of volume creation. " + str(n) + " seconds have passed\n")
            check=src_cmd+'cinder list'
            p=subprocess.check_output(check,shell=True)
            for line in re.findall('(.*)\n',p):
                line=line.rstrip('\n')
                if(re.search(cname,line)):
                    line=re.sub(r"\|",r"",line)
                    info=line.split()
                    cid=info[0]
                    cname=info[2]
                    cstatus=info[1]
                    sys.stderr.write('Status of ' + cname + ' is ' + cstatus + ' with id ' + cid + '\n')
                    if(cstatus=="available"):
                        flag=1
                        break
        n=n+i
    if(flag==1):
        sys.stderr.write("VM setup for " + cname + " with ID " + cid + " successful.  Attaching to vm\n")
        attach_vm=src_cmd+"nova volume-attach " + vid + " " + cid
        sys.stderr.write(date_time() + attach_vm + "\n")
        subprocess.call(attach_vm,shell=True)
        mount_cmd="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ubuntu@" + vip + " \"sh -s\" < /home/ubuntu/TOOLS/Scripts/utility/mount.sh \"REFS_" + bid + "\""
        sys.stderr.write(date_time() + mount_cmd + "\n")
        subprocess.call(mount_cmd,shell=True)
    else:
        sys.stderr.write("Volume setup timeout for " + cname + "Check connection settings or increase wait time and try again\n")
    return flag
                            
if __name__ == "__main__":
    import argparse

    parser=argparse.ArgumentParser(description='Attaches cinder volume with references to existing vm')
    parser.add_argument('-sid','--snapshot-id',action='store',dest='sid',help='ID of snapshot.  Use cinder to find')
    parser.add_argument('-vid','--virt-mach',action='store',dest='vid',help='Virtual machine id.  Use Nova to find')
    parser.add_argument('-id','--BID',action='store',dest='bid',help='Bionimbpus project id')
    parser.add_argument('-s','--size',action='store',dest='size',help='Cinder reference size.  Recommended value 200 (in GB)')
    parser.add_argument('-ip','--ip_add',action='store',dest='ip',help='VM IP address')
    parser.add_argument('-w','--wait',action='store',dest='wait',help='Wait time before giving up on spawning an image.  Recommended value 300 (in seconds)')
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    inputs=parser.parse_args()
    sid=inputs.bid
    vid=inputs.vid
    bid=inputs.bid
    size=inputs.size
    wait=inputs.wait

    attach_cinder(sid,vid,bid,size,vip,wait)