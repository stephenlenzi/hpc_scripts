# Brainreg array batch script file creation

Using the following function will write an array job file and will also create
a file called commands.txt with a list of all the commands that will be run when the array script is launched.

Its probably important not to edit this file while the job is running.

Existing output directories are skipped.

Rawdata directory is assumed to be in NIU neuroblueprint format: https://neuroblueprint.neuroinformatics.dev/latest/specification.html 

probably the only things that matter are:

- rawdata folder contains a folder for each mouse
- derivatives data is the same as the rawdata folder but with /rawdata/ replaced by /derivatives/ (changing this might break things)


```
def save_array_job(rawdata_directory, 
                   serial2p_directory_raw,
                   array_job_outpath="/ceph/margrie/slenzi/batch_scripts/", 
                   func=brainreg_command,
                   time_limit="3-0:0",
                   n_jobs=10,
                   n_jobs_at_a_time=4,
                   user_email="ucqfsle@ucl.ac.uk"
                   ):

```

# DLC on the HPC 

## Installation 


Instructions for using the HPC for DLC

```ssh user@ssh.swc.ucl.ac.uk```

```ssh user@hpc-gw1```

Then activate an interactive session on a cluster node for installing DLC:

```srun -p gpu --gres=gpu:1 -n 10 --pty bash -i```

```module load /ceph/apps/ubuntu-20/modulefiles/miniconda/4.9.2```

```module load /ceph/apps/ubuntu-20/modulefiles/cuda/11.2```

```export DLClight=True```

Create a conda environment with all the code you want installed

```conda create -n dlc python=3.9```

```source activate dlc```

```git clone https://github.com/stephenlenzi/hpc_scripts```

```cd /path/to/hpc_scripts```

```pip install -e .```

To test this:

```python```

```>>> import tensorflow as tf```

```>>> tf.test.is_gpu_available()```

should return True if configured correctly.

## Running scripts

To run scripts you should submit jobs via slurm. For this you will need to have your python code
installed remotely and you will need a batch script, written in bash, that will be used to call jobs on
the HPC.

First SSH to the swc network.

```ssh user@ssh.swc.ucl.ac.uk```

SSH again to the hpc.

```ssh user@hpc-gw1```

Then you will need to edit the bash script to run your code as a batch job on the cluster.

```sbatch run_dlc_training.sh```
















