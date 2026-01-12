from pathlib import Path, PurePosixPath


def load_experiment_directories(rawdata_dir):
    paths = list(Path(rawdata_dir).glob("*"))
    return paths


def load_session_directories(rawdata_dir):
    paths = list(Path(rawdata_dir).rglob("ses*"))
    return paths


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


def array_script_template(path_to_commands_ceph_remote_root="/ceph/margrie/slenzi/batch_scripts/commands.txt",
                          n_jobs=10,
                          n_jobs_at_a_time=4,
                          user_email="ucqfsle@ucl.ac.uk",
                          output_file_name="brainreg",
                          time_limit="3-0:0",
                          memory_limit=60,
                          module_strings=["brainglobe/2024-03-01",],
                          additional_commands=["",],
                          conda_environment_strings=["",],
                          ):

    module_loads = "\n".join([f"module load {x}" for x in module_strings])
    extra_cmds = "\n".join([f"{x}" for x in additional_commands])
    conda_cmds = "\n".join([f"conda activate {x}" for x in conda_environment_strings])

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

echo "Loading modules"
{module_loads}
{conda_cmds}
{extra_cmds}

cmd=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" {path_to_commands_ceph_remote_root})

echo "Running command: $cmd"
eval $cmd
"""
    return template


# def array_script_template_deeplabcut(path_to_commands_ceph_remote_root="/ceph/margrie/slenzi/batch_scripts/commands.txt",
#                           n_jobs=10,
#                           n_jobs_at_a_time=4,
#                           user_email="ucqfsle@ucl.ac.uk",
#                           output_file_name="deeplabcut",
#                           time_limit="3-0:0",
#                           memory_limit=60,
#                           module_strings=["deeplabcut/2022-07-06",]
#                           ):

#     template= f"""#!/bin/bash
# #
# #SBATCH -p gpu # partition (queue)
# #SBATCH -N 1   # number of nodes
# #SBATCH --mem {memory_limit}G # memory pool for all cores
# #SBATCH --gres=gpu:1
# #SBATCH -t {time_limit}
# #SBATCH -o logs/output_{output_file_name}_%A_%a.out
# #SBATCH -e logs/error_{output_file_name}_%A_%a.err
# #SBATCH --mail-type=ALL
# #SBATCH --mail-user={user_email}
# #SBATCH --array=0-{n_jobs}%{n_jobs_at_a_time}

# echo "Loading modules"
# {"".join([f"module load {x}\n" for x in module_strings])}

# cmd=$(sed -n "$((SLURM_ARRAY_TASK_ID+1))p" {path_to_commands_ceph_remote_root})

# echo "Running command: $cmd"
# eval $cmd
# """
#     return template



def load_session_directories(rawdata_directory):
    if rawdata_directory is None:
        print("No directory selected")
        return
    paths = list(Path(rawdata_directory).rglob("ses*"))
    session_directories=[path for path in paths if path.is_dir()]
    return session_directories


def merge_paths_to_linux_path(base_path, other_path):
    """
    Convert paths to Linux format, handling Mac mount points.
    
    If other_path is on a Mac mount point (/Volumes/...), it will replace
    the /Volumes/{volume_name}/ prefix with base_path. Otherwise, it preserves
    the path structure or merges paths relative to base_path.
    """
    base = Path(base_path)
    other = Path(other_path)
    
    # Check if other_path is on a Mac mount point (/Volumes/...)
    if other.is_absolute() and len(other.parts) >= 3:
        if other.parts[1] == 'Volumes' and base.is_absolute():
            # Extract the volume name (e.g., 'margrie' from '/Volumes/margrie/...')
            volume_name = other.parts[2]
            # Replace /Volumes/{volume_name}/ with base_path
            remaining_parts = other.parts[3:]
            merged = base
            for part in remaining_parts:
                merged = merged / part
            parts = [part for part in merged.parts if part not in ('\\', '')]
            return PurePosixPath('/', *parts)
    
    # Original logic for other cases
    try:
        rel = other.relative_to(base)
        merged = base / rel
    except ValueError:
        if other.is_absolute():
            merged = base.joinpath(*other.parts[1:])
        else:
            merged = base / other

    parts = [part for part in merged.parts if part not in ('\\', '')]
    return PurePosixPath('/', *parts)



def clear_file(array_job_commands_outpath):
    with open(str(array_job_commands_outpath), "w") as f:
        pass


def write_commands_to_file(array_job_commands_outpath, commands):
    with open(str(array_job_commands_outpath), "a") as f:
        if isinstance(commands,str):
            f.write(commands + "\n")
        else:
            for cmd in commands:
                f.write(cmd + "\n")


def write_batch_script(array_job_script_outpath, script_contents):
    with open(str(array_job_script_outpath), "w") as f:
        f.write(script_contents)
