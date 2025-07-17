# Brainreg array batch script file creation

Using the following function will write an array job file and will also create
a file called commands.txt with a list of all the commands that will be run when the array script is launched.

Its probably important not to edit this file while the job is running.

Existing output directories are skipped.

Rawdata directory is assumed to be in NIU neuroblueprint format: https://neuroblueprint.neuroinformatics.dev/latest/specification.html 

probably the only things that matter are:

- rawdata folder contains a folder for each mouse
- derivatives data is the same as the rawdata folder but with /rawdata/ replaced by /derivatives/ (changing this might break things)
- whole brain images can be kept in a different location to the "rawdata" and this should work as long as the mouse folder names match.. 

Look in hpc_scripts/brainreg/brainreg_array_job_constructor.py and edit the arguments in the main() function. Make sure to edit the email 
so it isn't mine or I'll get all the notifications when it runs. Also the paths to the data should be changed to yours.

```
def save_array_job(
                   rawdata_directory = Path("/ceph/margrie/slenzi/2025/dr/photometry/rawdata/"),   
                   serial2p_directory_raw = Path("/ceph/margrie/slenzi/serial2p/whole_brains/raw/"),
                   array_job_outpath="/ceph/margrie/slenzi/batch_scripts2/", 
                   func=brainreg_command,
                   time_limit="3-0:0",
                   n_jobs=10,
                   n_jobs_at_a_time=4,
                   user_email="ucqfsle@ucl.ac.uk",
                   atlas="allen_mouse_10um",
                   overwrite_existing=False,
                   )

```


## Running scripts

To run scripts you should submit jobs via slurm. For this you will need to have your python code
installed remotely and you will need a batch script, written in bash, that will be used to call jobs on
the HPC.

First SSH to the swc network.

```ssh user@ssh.swc.ucl.ac.uk```

SSH again to the hpc.

```ssh user@hpc-gw2```

Then call the sbatch command on the batch script file.

```sbatch /path/to/batch_script.sh```
















