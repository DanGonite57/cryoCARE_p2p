#! python
import argparse
import json
import warnings
import os
import sys
import random
from cryocare.internals.CryoCAREDataModule import CryoCARE_DataModule


def custom_formatwarning(msg, *args, **kwargs):
    # ignore everything except the message
    return str(msg) + '\n'


warnings.formatwarning = custom_formatwarning


def main():
    parser = argparse.ArgumentParser(description='Load training data generation config.')
    parser.add_argument('--conf')

    args = parser.parse_args()
    with open(args.conf, 'r') as f:
        config = json.load(f)

    if config.get("folders"):
        odd = []
        for folder in config["folders"]:
            odd += [os.path.join(folder, x) for x in os.listdir(folder) if "_ODD.mrc" in x]
        config["odd"] = random.sample(odd, config["num_slices"])
        config["even"] = [x.replace("_ODD.mrc", "_EVN.mrc") for x in config["odd"]]

    dm = CryoCARE_DataModule()
    dm.setup(config['odd'], config['even'], mask_paths=config['mask'] if 'mask' in config else None, n_samples_per_tomo=config['num_samples'],
                             validation_fraction=(1.0 - config['split']), sample_shape=config['patch_shape'],
                             tilt_axis=config['tilt_axis'], n_normalization_samples=config['n_normalization_samples'])
    
    try:
        os.makedirs(config['path'])
    except OSError:
        if 'overwrite' in config and config['overwrite']:
            os.makedirs(config['path'], exist_ok=True)
        else:
            print("Output directory already exists. Please choose a new output directory or set 'overwrite' to 'true' in your configuration file.")
            sys.exit(1)
            
    dm.save(config['path'])


if __name__ == "__main__":
    # execute only if run as a script
    main()
