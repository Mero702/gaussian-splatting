import os
import time
import uuid
from argparse import ArgumentParser

scenes = []
scenes_mip = ["bicycle", "bonsai", "counter", "flowers", "garden", "kitchen", "room", "stump", "treehill"]
scenes_synth = ["chair", "drums", "ficus", "hotdog", "lego", "materials", "mic", "ship"]
scenes_mvs = ["scene1", "scene6"]

#scenes = ["bonsai", "counter"]

commands = ["python train.py --eval", 
    "python train.py --eval --adc ema", 
    "python train.py --eval --adc var --densify_grad_threshold 0.000125",
    "python train.py --eval --adc direction --densify_grad_threshold 0.000125 --motion_efficiency_threshold 0.5"
    ]

parser = ArgumentParser(description="Full evaluation script parameters")
parser.add_argument("--m", default=0 , type=int)
parser.add_argument("--mip", type=str, help="Path to Mip-NeRF 360 dataset", default="../360")
parser.add_argument("--synth", type=str, help="Path to Synthesized dataset", default="../nerf_synthetic")
parser.add_argument("--mvs", type=str, help="Path to MVS dataset", default="../mvs")
parser.add_argument("--dataset", type=str, help="Dataset to evaluate on, either 'mip', 'synth', or 'mvs'", default="mip", choices=["mip", "synth", "mvs", "all"])
parser.add_argument("--name", type=str, help="Name of the evaluation run, used for output directory naming")
parser.add_argument("--fix_step", type=int, help="It will skip the first N steps", default=0)

args = parser.parse_args()
if args.dataset == "mip" or args.dataset == "all":
    for x in scenes_mip:
        scenes.append([x, args.mip+"/"+x])
if args.dataset == "synth" or args.dataset == "all":
    for x in scenes_synth:
        scenes.append([x, args.synth+"/"+x])
if args.dataset == "mvs" or args.dataset == "all":
    for x in scenes_mvs:
        scenes.append([x, args.mvs+"/"+x])
## randomized id
if args.name is not None:
    unique_str = args.name
else:
    if os.getenv('OAR_JOB_ID'):
        unique_str=os.getenv('OAR_JOB_ID')
    else:
        unique_str = str(uuid.uuid4())
path = os.path.join("./eval/", unique_str[0:10])

if args.fix_step < 1:
    for scene in scenes:
        cmd = commands[args.m] + " -s " + scene[1] + "/ -m "+path+"/" + scene[0]
        os.system(cmd)

if args.fix_step < 2:
    for scene in scenes:
        os.system("python render.py -m " + path + "/" + scene[0])

if args.fix_step < 3:
    for scene in scenes:
        os.system("python metrics.py -m " +  path + "/" + scene[0])




