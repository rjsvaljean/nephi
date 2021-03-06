__author__ = 'onina'

# execute this script from the home directory i.e. python nps/finetune.py 0 0 
# Given the best trained mode, this script will submit jobs to the queue and finetune such models
# based on the tasks and pages. Right now it is manually switched to the models, todo: add variable for different models
import os
import sys
from time import gmtime, strftime
import os
import sys
from glob import glob
import shutil
import subprocess

def create_qsub_file(name, bash_command):
    filename =  "pbs/icfhr/finetune/"+name + '.pbs'
    f = open(filename, 'w')
    f.write("#!/bin/bash \n")
    f.write("#PBS -A AFSNW35489ANO\n")
    f.write("#PBS -l select=1:ncpus=28:ompthreads=8:ngpus=2\n")
    f.write("#PBS -q GPU_RD\n")
    f.write("#PBS -l walltime=01:00:00\n")
    f.write("#PBS -N " + name + "\n")
    f.write("#PBS -j oe\n")
    f.write("source /home/oliver/.personal.bashrc\n")
    f.write("cd /p/home/oliver/projects/nephi\n")
    f.write(bash_command+"\n")
    f.write("exit\n")
    f.close()


    return filename

def submit_qsub(filename):
    os.system("cd pbs/icfhr/finetune")
    command = 'qsub ' + filename
    print(command)
    print(filename)
    os.system(command)

def main(argv):

    DEBUG = int(argv[1])

    lmdb_database_base = "data/lmdb_ICFHR_bin/specific_data_each_doc/"
    spec_tr_lists_dir = "data/datasets/read_ICFHR/specific_data_train_list/"

    spec_lists_files = glob(os.path.join(spec_tr_lists_dir, "*"))
    
    dirs = [os.path.basename(f).partition(".lst")[0] for f in spec_lists_files]

    lmdb_database_base = "data/lmdb_ICFHR_bin/specific_data_each_doc/"
    pre_model = "results_icfhr_aug/ctc_pretrain/netCNN_28_2982.pth"
    # pre_model = "results_icfhr_aug/attention+ctc/netCNN_24_2982.pth"

    

    idx = int(argv[2])
    for num in set([d.partition("_train_")[0] for d in dirs]):
        for s in ["1", "4", "16"]:
            # bash_command = ' '.join(["python crnn_main.py", "--trainroot", os.path.join(lmdb_database_base, num + "_train_" + s),
                               # "--valroot", os.path.join(lmdb_database_base, num + "_train_" + "8"),
                               # "--dataset ICFHR --cuda --lr 0.0001 --displayInterval 4 --valEpoch 1 --saveEpoch 1 --workers 3",
                               # "--niter 60 --keep_ratio --imgH 60 --imgW 240 --batchSize 4",
                               # "--transform --rescale --rescale_dim 3 --grid_distort",
                               # "--model attention+ctc --plot",
                               # "--rdir", "experiments/7May_finetuning/expr_" + "ICFHR_7May_finetuning_attention+ctc_" + num + "_train_" + s,
                               # "--pre_model",  pre_model, ">",
                               # "logs/icfhr/finetune/log_ICFHR_7May_finetuning_attention+ctc_" + num + "_train_" + s + ".txt"])
            bash_command = ' '.join(["python crnn_main.py", "--trainroot", os.path.join(lmdb_database_base, num + "_train_" + s),
                               "--valroot", os.path.join(lmdb_database_base, num + "_train_" + "8"),
                               "--dataset ICFHR --cuda --lr 0.0001 --displayInterval 4 --valEpoch 1 --saveEpoch 1 --workers 3",
                               "--niter 60 --keep_ratio --imgH 60 --imgW 240 --batchSize 4",
                               "--transform --rescale --rescale_dim 3 --grid_distort",
                               "--model ctc_pretrain --plot",
                               "--rdir", "experiments/7May_finetuning/expr_" + "ICFHR_7May_finetuning_ctc_pretrain_" + num + "_train_" + s,
                               "--pre_model",  pre_model, ">",
                               "logs/icfhr/finetune/log_ICFHR_7May_finetuning_ctc_pretrain_" + num + "_train_" + s + ".txt"])
            if DEBUG:
                print(bash_command)
                filename = create_qsub_file(str(idx), bash_command)
                # submit_qsub(filename)
                sys.exit(0)

            else:
                filename = create_qsub_file(str(idx),bash_command)
                submit_qsub(filename)

            idx+=1

if __name__=="__main__":


   main(sys.argv)
