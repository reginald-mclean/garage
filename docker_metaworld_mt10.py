import docker
from docker.types import DeviceRequest, Mount
import time
import os
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='launch ml10 experiments')
parser.add_argument('algo', metavar='a', type=str, default="mtsac", help='algorithm that will be launched')
args = parser.parse_args()
algo = args.algo

home = os.path.expanduser("~")

if not os.path.exists(f'{home}/metaworld-runs-v2'):
    os.makedirs(f'{home}/metaworld-runs-v2')

client = docker.from_env()

volume = Mount(f"{home}/code/garage/data", f"{home}/metaworld-runs-v2/", type='bind')
mjkey = open(f'{home}/.mujoco/mjkey.txt', 'r').read()
environment_vars = [f"MJKEY={mjkey}", "QT_X11_NO_MITSHM=1", "DISPLAY="]
device_requests = [DeviceRequest(count=-1, capabilities=[['gpu']])]


if algo=='mtsac':
    container = 'rlworkgroup/garage-nvidia'
    run_cmd = f'python metaworld_launchers/mt10/mtsac_metaworld_mt10.py'
else:
    raise ValueError("algorithm passed needs to be in {'mtsac'}")

seeds = np.random.randint(10000,size=(1,))
for seed in seeds:
    client.containers.run('rlworkgroup/garage-nvidia',
                          f'{run_cmd} --seed {seed}',
                          environment=environment_vars,
                          device_requests=device_requests,
                          mounts=[volume],
                          detach=True)
    time.sleep(0.1)
