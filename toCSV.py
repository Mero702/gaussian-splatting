import os
import time
import uuid
import re

from argparse import ArgumentParser


parser = ArgumentParser(description="Full evaluation script parameters")

parser.add_argument("--file", type=str, help="Path to the eval.txt file containing the evaluation results")

args = parser.parse_args()


re_name = re.compile(r"\.\/eval\/[0-9a-f-]+\/(\w+)")

re_train = re.compile(r"30000\/30000 \[(\d+:\d+)<[^P]+[\w]+=(\d+)")

re_metrics = re.compile(r"(?:SSIM|PSNR|LPIPS)(?: :|:)[\s]+(\d+.\d+)")
raw_result = []


print(f"Reading evaluation results from {args.file}...")

with open(args.file, 'r', encoding='utf-8') as file:
    lines = file.readlines()

    for line in lines:
        match_name = re_name.search(line)

        if match_name:
            raw_result.append(match_name.group(1))
        match_train = re_train.search(line)

        if match_train:
            raw_result.append(match_train.group(1))
            raw_result.append(match_train.group(2))
        match_metrics = re_metrics.search(line)

        if match_metrics:
            raw_result.append(match_metrics.group(1))


print("Extracted raw results: ", raw_result)

scenes = ["bicycle", "bonsai", "counter", "flowers", "garden", "kitchen", "room", "stump", "treehill", "chair", "drums", "ficus", "hotdog", "lego", "materials", "mic", "ship", "scene1", "scene6"]

class SceneData:
    def __init__(self):
        self.training_time = None
        self.gaussianCount = None
        self.metrics = []
    def toString(self, scene_name):
        if self.gaussianCount is not None:
            return f"{scene_name}: Training time: {self.training_time}, Gaussian Count: {self.gaussianCount}, Metrics: {self.metrics}"
        else:
            return ""
    def to_csv_row(self, scene_name):
        if self.gaussianCount is None:
            return ""
        else:
            return f"{scene_name}, {self.training_time}, {self.gaussianCount}, {', '.join(self.metrics)}\n"
    

scene_data = {scene: SceneData() for scene in scenes}
last_scene = ""
for x in raw_result:
    line = []
    
    if x in scenes:
        last_scene = x
    elif last_scene != "":
        if ':' in x:
            scene_data[last_scene].training_time = x
        elif x.isdigit():
            scene_data[last_scene].gaussianCount = x
        else:
            scene_data[last_scene].metrics.append(x)

print("Organized scene data: ", "\n".join([s.toString(sn) for sn, s in scene_data.items()]))
print("Scene, Training Time, Gaussian Count, SSIM, PSNR, LPIPS")
print("".join([s.to_csv_row(sn) for sn, s in scene_data.items()]))

csv_file_path = os.path.join(os.path.dirname(args.file), os.path.basename(args.file).replace(".txt", "_summary.csv"))
with open(csv_file_path, 'w', encoding='utf-8') as csv_file:
    csv_file.write("Scene, Training Time, Gaussian Count, SSIM, PSNR, LPIPS\n")
    for scene_name, data in scene_data.items():
        csv_file.write(data.to_csv_row(scene_name))