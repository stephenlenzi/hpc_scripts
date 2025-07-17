
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
