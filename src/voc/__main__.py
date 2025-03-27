import os
import logging
import logging.config
from argparse import ArgumentParser, FileType
from shutil import move

import yaml
import cv2 as cv
from tqdm import tqdm

from voc.inference import Inference

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
    print(params)

    if not os.path.exists(inputs):
        print(ERR_ + f"No such file or directory at {inputs}")
        exit(2)
    image_files = []
    if os.path.isdir(inputs):
        image_files.extend(os.listdir(inputs))
    else:
        image_files.append(os.path.basename(inputs))
        inputs = os.path.dirname(inputs)

    output_res = os.path.join(outputs, "results")
    os.makedirs(outputs, exist_ok=True)
    os.makedirs(output_res, exist_ok=True)

    inference = Inference(params)
    iteration = tqdm(
        image_files, desc="Object extraction", total=len(image_files))

    num_processed = 0
    for image_file in iteration:
        file_path = os.path.join(inputs, image_file)
        image = cv.imread(file_path)
        images = inference(image)
        if not images:
            continue
        output_file = os.path.join(outputs, image_file)
        if not os.path.isfile(output_file):
            move(file_path, output_file)
        for i, img in enumerate(images):
            res_img = os.path.join(output_res, f"{image_file}.{i + 1}.png")
            cv.imwrite(res_img, img)
        tqdm.write(f"Image processed: {image_file}")
        num_processed += 1
    print(f"{num_processed} processed on {len(image_file)}")


if __name__ == '__main__':
    main()
