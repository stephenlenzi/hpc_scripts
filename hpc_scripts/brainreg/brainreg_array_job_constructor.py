from pathlib import Path

def voxel_sizes(recipe_path):
    import yaml

    with open(str(recipe_path), "r") as stream:
        try:
            params = yaml.safe_load(stream)
            return params["VoxelSize"]
        except yaml.YAMLError as exc:
            print(exc)


def get_brain_all_channels_paths(
    mouse_id,
    brain_dir,
):
    p=Path(brain_dir) / mouse_id / "stitchedImages_100"
    return list(p.glob("*"))

def brainreg_command(mouse_directory_derivatives, 
                     serial2p_directory_raw, 
                     function="brainreg", 
                     atlas="allen_mouse_10um", 
                     additional=None,
                     overwrite_existing=False,
                     ):

    input_paths = get_brain_all_channels_paths(mouse_directory_derivatives.stem, serial2p_directory_raw)
    brainreg_commands = []
    for input_path in input_paths:
        output_path = mouse_directory_derivatives / "anat" / atlas / input_path.stem
        
        if (not overwrite_existing) and output_path.parent.exists():
            print(f"Found existing directory {output_path.parent}... skipping...")
            return None
        
        print(input_path)
        print(output_path)
        recipe_path = list(input_path.parent.parent.glob("recipe*"))[0]
        voxels = voxel_sizes(recipe_path)
        additional = f"--additional {input_path.parent / additional}" if additional is not None else ""
        cmd = f"{function} {input_path} {output_path} {additional} -v {voxels['Z']} {voxels['X']} {voxels['Y']} --orientation psr --atlas {atlas}"
        brainreg_commands.append(cmd)
    return brainreg_commands


def save_batch_script_single_brain(
                                  mouse_directory_derivatives,
                                  serial2p_directory_raw,
                                  user_email="ucqfsle@ucl.ac.uk", 
                                  out_output_file_name="brainreg_1.out", 
                                  err_output_file_name="brainreg_1.err",
                                  time_limit="3-0:0",
                                  script_output_directory=Path("/nfs/nhome/live/slenzi/Desktop")
                                  ):

    brainreg_commands = brainreg_command(mouse_directory_derivatives, serial2p_directory_raw)
    for i, cmd in enumerate(brainreg_commands):

        script_contents=f"""#!/bin/bash
#
#SBATCH -p gpu # partition (queue)
#SBATCH -N 1   # number of nodes
#SBATCH --mem 60G # memory pool for all cores
#SBATCH --gres=gpu:1
#SBATCH -t {time_limit}
#SBATCH -o {out_output_file_name}
#SBATCH -e {err_output_file_name}
#SBATCH --mail-type=ALL
#SBATCH --mail-user={user_email}


echo "Loading Brainglobe module"
module load brainglobe/2024-03-01

echo "Running brainreg"

{cmd}
                
            """
        print(f"saving {script_output_directory / f"brainreg_batch_{i}.sh"}")
        print(script_contents)

        with open(script_output_directory / f"brainreg_batch_{i}.sh", "w") as file:
            file.write(script_contents)


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

def load_experiment_directories(rawdata_dir):
    paths = list(Path(rawdata_dir).glob("*"))
    mouse_ids = [path.stem for path in paths if path.is_dir()]
    return paths, mouse_ids

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
                   array_job_outpath="/ceph/margrie/slenzi/batch_scripts/", 
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

