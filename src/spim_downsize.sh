#!/bin/env bash
#
#SBATCH -c 12                      # number of cores
#SBATCH -t 600
#SBATCH -o logs/smartspim_dsz_%j.out        # STDOUT #add _%a to see each array job
#SBATCH -e logs/smartspim_dsz_%j.err        # STDERR #add _%a to see each array job
#SBATCH --contiguous #used to try and get cpu mem to be contigous
#SBATCH --mem 120000

echo "In the directory: `pwd` "
echo "As the user: `whoami` "
echo "on host: `hostname` "

cat /proc/$$/status | grep Cpus_allowed_list

module load anacondapy/2020.11
module load elastix/4.8
. activate lightsheet

python spim_downsize.py "$1" "$2" "$3"

#functionality
#takes 3 command line arguments max
#stepid = int(sys.argv[1]) - regular or inverse transform, mostly just need inverse for cells/atlas
#src = str(sys.argv[2]) - folder to stitched images, e.g. /jukebox/LightSheetTransfer/tp/20200701_12_55_28_20170207_db_bl6_crii_rpv_01/
#reg = str(sys.argv[3]) - folder fo registration channel, e.g. Ex_488_Em_0
