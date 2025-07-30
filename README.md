#HPC SCRIPTS

## Installation

Install within your favourite e.g. conda environment.

```
git clone https://github.com/stephenlenzi/hpc_scripts.git
cd hpc_scripts
pip install -e .
```


## Brainglobe array batch script file creation

Using the following function will write an array job file (batch script) and will also create
a file called commands.txt with a list of all the commands that will be run when the array script is launched.

- Don't edit this file while the job is running.
- Existing output directories are skipped by default.
- Rawdata directory is assumed to be in NIU neuroblueprint format: https://neuroblueprint.neuroinformatics.dev/latest/specification.html 

Ideally:

- Rawdata folder contains a folder for each mouse
- Derivatives data is the same folder hierarchy as the rawdata folder but with /rawdata/ replaced by /derivatives/.
- Whole brain images can be kept in a different location to the "rawdata" and this should work as long as the mouse folder names match.


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


Look in hpc_scripts/brainglobe_array_job_constructor.py and edit the arguments in the main() function. Also the paths to the data should be changed to yours.

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
```python -m hpc_scripts.brainglobe_array_job_constructor```


## Brainglobe array batch script file creation GUI

For convenience there is a GUI where you can select which mice to add to the batch script for processing.
By default anything that has been processed will not be added anyway. This needs to be run locally, so if you 
have ceph mounted locally this should convert all paths to /ceph/ format.

To launch the gui:
```python -m hpc_scripts.gui```

<img width="781" height="758" alt="image" src="https://github.com/user-attachments/assets/2de75d6c-7f75-424f-8715-4d09fdac7285" />


CRITICAL: the path to remote data folder should be set to the full path from /ceph/ up to the folder you have mounted. Usually this is the lab folder i.e.  /ceph/margrie/.

When you set the raw data directory, the derivatives directory will be updated to the expected location, and the table should be populated with a list of mouse ids, or whatever the subfolders are called.

You then need to select the mouse ids that you want to be included in the batch script, and then tick the box for brainreg or cellfinder. Then when you are happy, click run, this will lead to a batch script.sh and a commands file.txt. These should contain paths relative to /ceph/ which is the expected format on the hpc, rather than any custom mounts.

### Custom modules
If you want to use custom modules from the GUI this is doable. You need to set the path to the modulefiles and they will be read out and put as options.
You can select as many as you like and it will execute them all.

<img width="868" height="39" alt="image" src="https://github.com/user-attachments/assets/4c7fb8df-63fb-456a-bcf4-b8e5f28990ee" />

<img width="843" height="179" alt="image" src="https://github.com/user-attachments/assets/234ffaf8-ee00-49f2-b440-abff6b036d7b" />


### Example output

You should get two files out - one that stores the command for each slurm job as a single line e.g. "commands_brainreg.txt" and another
that contains the batch script for running those commands e.g. "array_job_brainreg.sh".

#### Array job brainreg example
```
#!/bin/bash
#
#SBATCH -p gpu # partition (queue)
#SBATCH -N 1   # number of nodes
#SBATCH --mem 60G # memory pool for all cores
#SBATCH --gres=gpu:1
#SBATCH -t 3-0:0
#SBATCH -o logs/output_brainreg_%A_%a.out
#SBATCH -e logs/error_brainreg_%A_%a.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=
#SBATCH --array=0-10%4

echo "Loading Brainglobe module"
module load brainglobe/2024-03-01

cmd=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" /ceph/margrie/slenzi/batch_scripts/commands_brainreg.txt)

echo "Running command: $cmd"
eval $cmd
```
#### Brainreg commands output example
```
brainreg /ceph/margrie/slenzi/serial2p/whole_brains/raw/sub-015_id-1105605_type-sertcregcampdr/stitchedImages_100/3 /ceph/margrie/slenzi/2025/dr/photometry/derivatives/sub-015_id-1105605_type-sertcregcampdr/anat/allen_mouse_10um/3  -v 25.0 2.504 2.504 --orientation psr --atlas allen_mouse_10um
brainreg /ceph/margrie/slenzi/serial2p/whole_brains/raw/sub-015_id-1105605_type-sertcregcampdr/stitchedImages_100/2 /ceph/margrie/slenzi/2025/dr/photometry/derivatives/sub-015_id-1105605_type-sertcregcampdr/anat/allen_mouse_10um/2 --additional /ceph/margrie/slenzi/serial2p/whole_brains/raw/sub-015_id-1105605_type-sertcregcampdr/stitchedImages_100 -v 25.0 2.504 2.504 --orientation psr --atlas allen_mouse_10um


... etc

```
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
