#HPC SCRIPTS

## Installation


```
git clone https://github.com/stephenlenzi/hpc_scripts.git
cd hpc_scripts
pip install -e .
```


## Brainglobe array batch script file creation

Using the following function will write an array job file and will also create
a file called commands.txt with a list of all the commands that will be run when the array script is launched.

Its probably important not to edit this file while the job is running.

Existing output directories are skipped.

Rawdata directory is assumed to be in NIU neuroblueprint format: https://neuroblueprint.neuroinformatics.dev/latest/specification.html 

probably the only things that matter are:

- rawdata folder contains a folder for each mouse
- derivatives data is the same as the rawdata folder but with /rawdata/ replaced by /derivatives/ (changing this might break things)
- whole brain images can be kept in a different location to the "rawdata" and this should work as long as the mouse folder names match.. 


Go to hpc_scripts/slurm_config and set the parameters according to your need. Make sure to edit the email to be your email


```
slurm_params = {
    "time_limit": "3-0:0", # 3 days, 0 hours, 0 minutes
    "n_jobs": 10,
    "n_jobs_at_a_time": 4,
    "user_email": "",
    "memory_limit": 60,

}

```


Look in hpc_scripts/brainreg_array_job_constructor.py and edit the arguments in the main() function. Also the paths to the data should be changed to yours.

CRITICAL: This must be run from somewhere with a direct ceph mount (i.e. path should look like /ceph/lab/user/data), and
wont work on e.g. windows with ceph mount. If you want to run locally use the GUI (see below).

```

def main():
    atlas = "allen_mouse_10um"
    overwrite_existing=False
    rawdata_directory = Path("/path/to/rawdata/")   
    serial2p_directory_raw = Path("/path/to/whole_brains/")
    array_job_outpath=Path("/path/to/batch_scripts/")


```


To run the script:
```python -m hpc_scripts.brainreg_array_job_constructor```

## Brainglobe array batch script file creation GUI

For convenience there is a GUI where you can select which mice to add to the batch script for processing.
By default anything that has been processed will not be added anyway. This needs to be run locally, so if you 
have ceph mounted locally this should convert all paths to /ceph/ format.

To launch the gui:
```python -m hpc_scripts.gui```

<img width="781" height="758" alt="image" src="https://github.com/user-attachments/assets/2de75d6c-7f75-424f-8715-4d09fdac7285" />


### Running scripts

To run scripts you should submit jobs via slurm. For this you will need to have your python code
installed remotely and you will need a batch script, written in bash, that will be used to call jobs on
the HPC.

First SSH to the swc network.

```ssh user@ssh.swc.ucl.ac.uk```

SSH again to the hpc.

```ssh user@hpc-gw2```

Then call the sbatch command on the batch script file.

```sbatch /path/to/batch_script.sh```
