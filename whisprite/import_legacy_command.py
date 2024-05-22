### THIS SCRIPT IS MEANT TO BE RUN MANUALLY FOR DATA IMPORT
### AND NOT BY THE END USER

import argparse
import asyncio
import json
from datetime import datetime
import os
from typing import List

import twitchio
from dotenv import load_dotenv

from whisprite.db.models.commands import UserCommand, CommandAlias

load_dotenv()


def _main(args: argparse.Namespace) -> None:
    commands = []
    aliases = []

    with open(args.infile) as f:
        for line in f:
            data = json.loads(line.strip())

            commands.append(UserCommand(name=data["_id"], content=data["output"]))

            for alias in data["aliases"]:
                aliases.append(CommandAlias(name=alias, target=data["_id"]))

    UserCommand.bulk_create(commands)
    CommandAlias.bulk_create(aliases)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    args = parser.parse_args()

    _main(args)
