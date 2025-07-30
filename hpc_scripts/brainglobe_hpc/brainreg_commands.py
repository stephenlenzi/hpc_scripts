from pathlib import Path
from hpc_scripts.brainglobe_hpc.shared_functions import voxel_sizes, get_brain_all_channels_paths, \
    array_script_template, load_experiment_directories, merge_paths_to_linux_path,  clear_file, \
    write_commands_to_file, write_batch_script
from hpc_scripts.slurm_config import slurm_params


def brainreg_command(mouse_directory_derivatives, 
                     serial2p_directory_raw,
                     ceph_path_root,
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

        recipe_path = list(input_path.parent.parent.glob("recipe*"))[0]
        voxels = voxel_sizes(recipe_path)

        print(input_path)
        print(output_path)
        if ceph_path_root is not None:
            input_path = merge_paths_to_linux_path(ceph_path_root, input_path)
            output_path = merge_paths_to_linux_path(ceph_path_root, output_path)

        print(input_path)
        print(output_path)

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
                            atlas="allen_mouse_10um",
                            slurm_params=slurm_params,
                            mouse_ids_to_process=None,
                            ceph_path_root=None,
                            module_strings=None,
                            ):
    

    array_job_commands_outpath = Path(array_job_outpath) / "commands_brainreg.txt"
    array_job_script_outpath = Path(array_job_outpath) / "array_job_brainreg.sh"
    
    clear_file(array_job_commands_outpath)

    all_directories = load_experiment_directories(rawdata_directory) if mouse_ids_to_process is None else get_paths_from_mouse_ids(rawdata_directory, mouse_ids_to_process)

    for mouse_directory_rawdata in all_directories:
        mouse_directory_derivatives = Path(str(mouse_directory_rawdata).replace("rawdata", "derivatives"))

        brainreg_commands = brainreg_command(
                                             mouse_directory_derivatives,
                                             serial2p_directory_raw,
                                             ceph_path_root,
                                             atlas=atlas,
                                             overwrite_existing=overwrite_existing,
                                            )
        
        if brainreg_commands is not None:
            write_commands_to_file(array_job_commands_outpath, brainreg_commands)
    path_to_commands_ceph_remote_root = merge_paths_to_linux_path(ceph_path_root, array_job_commands_outpath) if ceph_path_root is not None else array_job_commands_outpath
    array_script = array_script_template(
                          path_to_commands_ceph_remote_root=path_to_commands_ceph_remote_root,
                          n_jobs=slurm_params["n_jobs"],
                          n_jobs_at_a_time=slurm_params["n_jobs_at_a_time"],
                          user_email=slurm_params["user_email"], 
                          output_file_name="brainreg", 
                          time_limit=slurm_params["time_limit"],
                          memory_limit=slurm_params["memory_limit"],
                          module_strings=module_strings,
    )
    write_batch_script(array_job_script_outpath, array_script)



