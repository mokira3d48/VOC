import os
import logging
import logging.config
from argparse import ArgumentParser, FileType

import yaml

logging.config.fileConfig('logging.conf')
LOG = logging.getLogger('voc')
ERR_ = '[\033[91mERR\033[0m] '
WAN_ = '[\033[91mWAN\033[0m] '


def main():
    """Main function"""
    parser = ArgumentParser(prog="VOC")
    parser.add_argument(
        'params', type=FileType(mode='r'), help="YAML config file.")
    parser.add_argument(
        '-i', '--input', type=str, required=True,
        help="Path to image file or image directory.")
    parser.add_argument('-o', '--output', type=str, help="Outputs directory.")
    args = parser.parse_args()

    params = yaml.safe_load(args.params)
    inputs = args.input
    outputs = args.output if args.output else 'outputs'

    if not os.path.exists(inputs):
        print(ERR_ + f"No such file or directory at {inputs}")
        exit(2)
    image_files = []
    if os.path.isdir(inputs):
        image_files.extend(os.listdir(inputs))
    else:
        image_files.append(os.path.basename(inputs))
        inputs = os.path.dirname(inputs)
    os.makedirs(outputs, exist_ok=True)




if __name__ == '__main__':
    main()
