import argparse
import pickle
import random
import time
from pathlib import Path

import gym
from gym.wrappers import RecordEpisodeStatistics
import numpy as np
import torch

from ddqn_per import DDQNPER

model_cls = DDQNPER
model_name = "DDQNPER"

# Parse settings
parser = argparse.ArgumentParser(description="Train an RL model for target control.")
parser.add_argument(
    "--time-steps", metavar="N", type=int, help="Total number of training time steps."
)
parser.add_argument(
    "--seed", type=int, default=42, metavar="S", help="random seed (default: 42)."
)
parser.add_argument("--env", type=str, help="the environment to run.")
parser.add_argument(
    "--resume-training",
    action="store_true",
    help="resume training from latest checkpoint.",
)
parser.add_argument("--checkpoint-dir", default="models", help="path to save models")
parser.add_argument(
    "--no-cuda", action="store_true", default=False, help="disables CUDA training"
)
parser.add_argument(
    "--eval-only", action="store_true", default=False, help="evaluate only"
)
parser.add_argument(
    "--exp-name", type=str, default="ddqn", metavar="E", help="the experiment name."
)
parser.add_argument("--log-dir", default="logs", help="path to save logs")
args = parser.parse_args()
use_cuda = not args.no_cuda and torch.cuda.is_available()
DEVICE = torch.device("cuda" if use_cuda else "cpu")
print(f"Training on {DEVICE}")

# Reproducibility
torch.manual_seed(args.seed)
np.random.seed(args.seed)
random.seed(args.seed)

# Load env
env = gym.make(args.env)
env = RecordEpisodeStatistics(env, deque_size=10)

# set up logs
TOP_LEVEL_LOG_DIR = Path(args.log_dir)
TOP_LEVEL_LOG_DIR.mkdir(parents=True, exist_ok=True)

RUN_NAME = f"{args.env.split('/')[1]}_{args.exp_name}_{args.seed}_{int(time.time())}"

# Checkpoints
checkpoint_path = Path(args.checkpoint_dir) / RUN_NAME
checkpoint_path.mkdir(parents=True, exist_ok=True)


def get_latest_checkpoint():
    model_checkpoints = Path(args.checkpoint_dir) / RUN_NAME

    files = list(model_checkpoints.glob("*.pt"))
    if len(files) > 0:
        return max(files, key=lambda x: x.stat().st_ctime)
    else:
        return None


# Model
total_time_steps = args.time_steps
resume_steps = None
model = DDQNPER(env, DEVICE)
resume_steps = 0
if args.resume_training:
    model_path = get_latest_checkpoint()

    if model_path:
        model = model_cls.load(model_path, env, device=DEVICE)
        resume_steps = total_time_steps - model.num_timesteps


if not args.eval_only:
    print(f"Training for {total_time_steps - resume_steps} time steps...")
    model.learn(
        total_time_steps,
        checkpoint_freq=10_000,
        checkpoint_path=checkpoint_path,
        resume_steps=resume_steps,
        log_dir=TOP_LEVEL_LOG_DIR,
        log_name=RUN_NAME,
        log=True,
    )
