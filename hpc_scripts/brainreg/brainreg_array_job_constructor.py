from pathlib import Path
from brainreg_commands import brainreg_command, get_brain_all_channels_paths, load_experiment_directories


def array_script_template(path_to_commands="/ceph/margrie/slenzi/batch_scripts/commands.txt", 
                          n_jobs=10,
                          n_jobs_at_a_time=4,
                          user_email="ucqfsle@ucl.ac.uk", 
                          output_file_name="brainreg", 
                          time_limit="3-0:0",
                          memory_limit=60,
                          ):

    template= f"""#!/bin/bash
#
#SBATCH -p gpu # partition (queue)
#SBATCH -N 1   # number of nodes
#SBATCH --mem {memory_limit}G # memory pool for all cores
#SBATCH --gres=gpu:1
#SBATCH -t {time_limit}
#SBATCH -o logs/output_{output_file_name}_%A_%a.out
#SBATCH -e logs/error_{output_file_name}_%A_%a.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user={user_email}
#SBATCH --array=0-{n_jobs}%{n_jobs_at_a_time}

echo "Loading Brainglobe module"
module load brainglobe/2024-03-01

cmd=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" {path_to_commands})

echo "Running command: $cmd"
eval $cmd
"""
    return template



def save_array_job(rawdata_directory, 
                   serial2p_directory_raw,
                   array_job_outpath="/ceph/margrie/slenzi/batch_scripts/", 
                   func=brainreg_command,
                   time_limit="3-0:0",
                   n_jobs=10,
                   n_jobs_at_a_time=4,
                   user_email="ucqfsle@ucl.ac.uk",
                   atlas="allen_mouse_10um",
                   overwrite_existing=False,
                   ):
    

    array_job_commands_outpath = Path(array_job_outpath) / "commands.txt"
    array_job_script_outpath = Path(array_job_outpath) / "array_job.sh"
    
    #delete previous file
    with open(str(array_job_commands_outpath), "w") as f:
        pass 

    all_directories, mouse_ids = load_experiment_directories(rawdata_directory)
    
    print(f"processing.. {mouse_ids}")
    
    for mouse_directory_rawdata in all_directories:
        mouse_directory_derivatives = Path(str(mouse_directory_rawdata).replace("rawdata", "derivatives"))
        brainreg_commands = func(mouse_directory_derivatives, 
                                 serial2p_directory_raw,
                                 atlas=atlas,
                                 overwrite_existing=False,
                                 )
        
        if brainreg_commands is not None:
            with open(str(array_job_commands_outpath), "a") as f:
                for cmd in brainreg_commands:
                    f.write(cmd + "\n")
        
    array_script = array_script_template(
                         path_to_commands=array_job_commands_outpath, 
                          n_jobs=n_jobs,
                          n_jobs_at_a_time=n_jobs_at_a_time,
                          user_email=user_email, 
                          output_file_name="brainreg", 
                          time_limit=time_limit,

    )

    with open(str(array_job_script_outpath), "w") as f:
        f.write(array_script_template(array_job_commands_outpath))


def main():
    save_array_job(
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
    
if __name__ == "__main__":
    main()

