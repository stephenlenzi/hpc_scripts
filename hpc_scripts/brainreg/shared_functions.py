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
