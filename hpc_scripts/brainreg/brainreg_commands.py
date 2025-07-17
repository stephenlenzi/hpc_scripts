from pathlib import Path


def load_experiment_directories(rawdata_dir):
    paths = list(Path(rawdata_dir).glob("*"))
    mouse_ids = [path.stem for path in paths if path.is_dir()]
    return paths, mouse_ids


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
