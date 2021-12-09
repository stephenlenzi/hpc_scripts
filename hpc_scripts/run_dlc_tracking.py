import fire
import pathlib
import deeplabcut


def run_dlc_training_steps(config_path, videos_dir, video_fname):
    p = pathlib.Path(videos_dir)
    video_paths = list(p.rglob(f'{video_fname}'))
    deeplabcut.analyze_videos(config_path, video_paths)


def main():
    fire.Fire(run_dlc_training_steps)


if __name__ == "__main__":
    main()

