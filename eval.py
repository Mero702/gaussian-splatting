import os
import time
import uuid
from argparse import ArgumentParser

scenes = ["bicycle", "bonsai", "counter", "flowers", "garden", "kitchen", "room", "stump", "treehill"]
#scenes = ["bonsai", "counter"]

commands = ["python train.py --eval", 
    "python train.py --eval --adc ema", 
    "python train.py --eval --adc var --densify_grad_threshold 0.000125"
    ]

parser = ArgumentParser(description="Full evaluation script parameters")
parser.add_argument("--m", default=0 , type=int)
parser.add_argument("--mip", type=str, help="Path to Mip-NeRF 360 dataset", default="./360")

args = parser.parse_args()
## randomized id

if os.getenv('OAR_JOB_ID'):
    unique_str=os.getenv('OAR_JOB_ID')
else:
    unique_str = str(uuid.uuid4())
path = os.path.join("./eval/", unique_str[0:10])

start_time = time.time()
for scene in scenes:
    cmd = commands[args.m] + " -s " + args.mip +"/"+ scene + "/ -m "+path+"/" + scene
    os.system(cmd)
total_time = (time.time() - start_time)/60.0
with open(os.path.join(path,"timing.txt"), 'w') as file:
    file.write(f"Total time: {total_time} minutes \n ")

for scene in scenes:
    os.system("python render.py -m " + path + "/" + scene)

for scene in scenes:
    os.system("python metrics.py -m " +  path + "/" + scene)




