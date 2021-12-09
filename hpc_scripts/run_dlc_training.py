import fire
import deeplabcut


def run_dlc_training_steps(config_path):
    deeplabcut.create_training_dataset(config_path, augmenter_type='imgaug')
    deeplabcut.train_network(config_path)
    deeplabcut.evaluate_network(config_path, Shuffles=[1], plotting=True)


def main():
    fire.Fire(run_dlc_training_steps)


if __name__ == "__main__":
    main()


