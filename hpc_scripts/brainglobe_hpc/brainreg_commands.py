from pathlib import Path
from brainglobe_hpc.shared_functions import voxel_sizes, get_brain_all_channels_paths, array_script_template, load_experiment_directories
from hpc_scripts.slurm_config import slurm_params


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

def get_paths_from_mouse_ids(rawdata_dir, mouse_ids):
    p = Path(rawdata_dir)
    return [p/mouse_id for mouse_id in mouse_ids]


def save_brainreg_array_job(rawdata_directory, 
                   serial2p_directory_raw,
                   array_job_outpath="/ceph/margrie/slenzi/batch_scripts/", 
                   overwrite_existing=False,
                   func=brainreg_command,
                   atlas="allen_mouse_10um",
                   slurm_params=slurm_params,
                   mouse_ids_to_process=None,
                   ):
    

    array_job_commands_outpath = Path(array_job_outpath) / "commands_brainreg.txt"
    array_job_script_outpath = Path(array_job_outpath) / "array_job_brainreg.sh"
    
    #delete contents of previous file
    with open(str(array_job_commands_outpath), "w") as f:
        pass 

    all_directories = load_experiment_directories(rawdata_directory) if mouse_ids_to_process is None else get_paths_from_mouse_ids(rawdata_directory, mouse_ids_to_process)
    print(f"all directories: {all_directories} ")
    print(f"all mice: {mouse_ids_to_process} ")
    for mouse_directory_rawdata in all_directories:
        mouse_directory_derivatives = Path(str(mouse_directory_rawdata).replace("rawdata", "derivatives"))
        brainreg_commands = func(mouse_directory_derivatives, 
                                 serial2p_directory_raw,
                                 atlas=atlas,
                                 overwrite_existing=overwrite_existing,
                                 )
        
        if brainreg_commands is not None:
            with open(str(array_job_commands_outpath), "a") as f:
                for cmd in brainreg_commands:
                    f.write(cmd + "\n")
        
    array_script = array_script_template(
                         path_to_commands=array_job_commands_outpath, 
                          n_jobs=slurm_params["n_jobs"],
                          n_jobs_at_a_time=slurm_params["n_jobs_at_a_time"],
                          user_email=slurm_params["user_email"], 
                          output_file_name="brainreg", 
                          time_limit=slurm_params["time_limit"],
                          memory_limit=slurm_params["memory_limit"],
    )

    with open(str(array_job_script_outpath), "w") as f:
        f.write(array_script_template(array_job_commands_outpath))