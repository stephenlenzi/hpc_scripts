from pathlib import Path
from hpc_scripts.brainglobe_hpc.shared_functions import voxel_sizes, get_brain_all_channels_paths, \
    load_experiment_directories, array_script_template, clear_file, write_commands_to_file, merge_paths_to_linux_path, \
    write_batch_script
from hpc_scripts.slurm_config import slurm_params

def cellfinder_command(mouse_directory_derivatives, 
                       serial2p_directory_raw,
                       ceph_path_root,
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
    print(f"input_paths: {len(input_paths)}")
    print(f"input_paths: {type(input_paths)}")

    for input_path in input_paths:
        output_path = mouse_directory_derivatives / "anat" / atlas / input_path.stem

        if (not overwrite_existing) and output_path.parent.exists():
            print(f"Found existing directory {output_path.parent}... skipping...")
            return None

        signal_path = input_path / signal_channel
        background_path = input_path / background_channel
        #output_path = mouse_directory_derivatives / "anat" / atlas / function
        print(input_path)
        print(type(input_path))
        print(output_path)
        print(type(output_path))


        recipe_path = list(input_path.parent.parent.glob("recipe*"))[0]
        if ceph_path_root is not None:
            output_path = merge_paths_to_linux_path(ceph_path_root, output_path)
            signal_path = merge_paths_to_linux_path(ceph_path_root, signal_path)
            background_path = merge_paths_to_linux_path(ceph_path_root, background_path)
            if model_path is not None:
                model_path = merge_paths_to_linux_path(ceph_path_root, Path(model_path))


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
                   atlas="allen_mouse_10um",
                   overwrite_existing=False,
                   slurm_params=slurm_params,
                   model_path=None,
                   ceph_path_root=None,
                   module_strings=["brainglobe/2024-03-01",],
                              ):
    

    array_job_commands_outpath = Path(array_job_outpath) / "commands_cellfinder.txt"
    array_job_script_outpath = Path(array_job_outpath) / "array_job_cellfinder.sh"

    clear_file(array_job_commands_outpath)

    all_directories = load_experiment_directories(rawdata_directory)
        
    for mouse_directory_rawdata in all_directories:
        mouse_directory_derivatives = Path(str(mouse_directory_rawdata).replace("rawdata", "derivatives"))
        cellfinder_commands = cellfinder_command(
                                                 mouse_directory_derivatives,
                                                 serial2p_directory_raw,
                                                 ceph_path_root,
                                                 atlas=atlas,
                                                 overwrite_existing=overwrite_existing,
                                                 model_path=model_path,
                                                 )
        
        if cellfinder_commands is not None:
            write_commands_to_file(array_job_commands_outpath, cellfinder_commands)
    path_to_commands_ceph_remote_root = merge_paths_to_linux_path(ceph_path_root, array_job_commands_outpath) \
        if ceph_path_root is not None else array_job_commands_outpath

    array_script = array_script_template(
                          path_to_commands_ceph_remote_root=path_to_commands_ceph_remote_root,
                          n_jobs=slurm_params["n_jobs"],
                          n_jobs_at_a_time=slurm_params["n_jobs_at_a_time"],
                          user_email=slurm_params["user_email"],
                          output_file_name="cellfinder",
                          time_limit=slurm_params["time_limit"],
                          memory_limit=slurm_params["memory_limit"],
    )

    write_batch_script(array_job_script_outpath, array_script)

