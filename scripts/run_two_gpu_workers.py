#!/usr/bin/env python3
"""Run two independent manifest-scoring commands, one per GPU."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    parser.add_argument("--gpus", nargs=2, default=("0", "1"))
    args = parser.parse_args()
    if not args.command:
        parser.error("Provide the scoring command after --")
    processes = []
    for shard_index, gpu in enumerate(args.gpus):
        environment = os.environ.copy()
        environment["CUDA_VISIBLE_DEVICES"] = gpu
        expanded = [
            part.replace("{shard}", str(shard_index)).replace("{gpu}", gpu)
            for part in args.command
        ]
        command = [
            *expanded,
            "--num-shards",
            "2",
            "--shard-index",
            str(shard_index),
        ]
        processes.append(subprocess.Popen(command, env=environment))
    return max(process.wait() for process in processes)


if __name__ == "__main__":
    sys.exit(main())
