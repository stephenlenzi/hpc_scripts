from pathlib import Path
from shared_functions import voxel_sizes, get_brain_all_channels_paths, load_experiment_directories, array_script_template
from slurm_config import slurm_params

def cellfinder_command(mouse_directory_derivatives, 
                       serial2p_directory_raw, 
                       function="cellfinder",
                       atlas="allen_mouse_10um", 
                       signal_channel='2', 
                       background_channel='4', 
                       model_path=None, 
                       logs_path=None,
                       overwrite_existing=False,
                       ):
    print(mouse_directory_derivatives)
    input_paths = get_brain_all_channels_paths(mouse_directory_derivatives.stem, serial2p_directory_raw)
    print(f"input_paths: {input_paths}")

    for input_path in input_paths:
        output_path = mouse_directory_derivatives / "anat" / atlas / input_path.stem

        signal_path = input_path / signal_channel
        background_path = input_path / background_channel
        #output_path = mouse_directory_derivatives / "anat" / atlas / function
        print(input_path)
        print(output_path)
        if (not overwrite_existing) and output_path.parent.exists():
            print(f"Found existing directory {output_path.parent}... skipping...")
            return None

        recipe_path = list(input_path.parent.parent.glob("recipe*"))[0]
        voxels = voxel_sizes(recipe_path)
        if function == 'cellfinder':
            additional = f"--trained-model {model_path}" if model_path is not None else ""
        elif function =='brainmapper':
            additional = f"--model-weights {model_path}" if model_path is not None else ""

        cmd = f"{function} -s {signal_path} -b {background_path} -o {output_path} --voxel-sizes {voxels['Z']} {voxels['X']} {voxels['Y']} {additional} --orientation psr --atlas {atlas}"
        return cmd



def save_cellfinder_array_job(rawdata_directory, 
                   serial2p_directory_raw,
                   array_job_outpath="/ceph/margrie/slenzi/batch_scripts/", 
                   func=cellfinder_command,
                   atlas="allen_mouse_10um",
                   overwrite_existing=False,
                   slurm_params=slurm_params,
                   ):
    

    array_job_commands_outpath = Path(array_job_outpath) / "commands_cellfinder.txt"
    array_job_script_outpath = Path(array_job_outpath) / "array_job_cellfinder.sh"
    
    #delete contents of previous file
    with open(str(array_job_commands_outpath), "w") as f:
        pass 

    all_directories, mouse_ids = load_experiment_directories(rawdata_directory)
    
    print(f"processing.. {mouse_ids}")
    
    for mouse_directory_rawdata in all_directories:
        mouse_directory_derivatives = Path(str(mouse_directory_rawdata).replace("rawdata", "derivatives"))
        cellfinder_commands = func(mouse_directory_derivatives, 
                                 serial2p_directory_raw,
                                 atlas=atlas,
                                 overwrite_existing=overwrite_existing,
                                 )
        
        if cellfinder_commands is not None:
            with open(str(array_job_commands_outpath), "a") as f:
                f.write(cellfinder_commands + "\n")
        
    array_script = array_script_template(
                          path_to_commands=array_job_commands_outpath, 
                          output_file_name="cellfinder", 
                          n_jobs=slurm_params["n_jobs"],
                          n_jobs_at_a_time=slurm_params["n_jobs_at_a_time"],
                          user_email=slurm_params["user_email"], 
                          time_limit=slurm_params["time_limit"],

    )

    with open(str(array_job_script_outpath), "w") as f:
        f.write(array_script_template(array_job_commands_outpath))

