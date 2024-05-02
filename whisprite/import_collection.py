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

from whisprite.db.models.collections import Collection, CollectionEntry

load_dotenv()


def _main(args: argparse.Namespace) -> None:
    client = twitchio.Client(token=os.environ["TWITCH_ACCESS_TOKEN"])
    collection = Collection.get(name=args.name)
    records = []

    loop = asyncio.new_event_loop()
    loop.run_until_complete(client.connect())
    with open(args.infile) as f:
        for line in f:
            data = json.loads(line.strip())
            timestamp = (
                datetime.fromtimestamp(data["timestamp"] / 1000)
                if data["timestamp"] is not None
                else None
            )

            user: List[twitchio.User] = loop.run_until_complete(
                client.fetch_users(
                    [data["author"] if data["author"] != "willowthewhispersr" else "ariaverge"]
                )
            )

            if not len(user):
                user = loop.run_until_complete(client.fetch_users(["whisprite"]))

            records.append(
                CollectionEntry(
                    collection=collection,
                    value=data[args.key],
                    created_at=timestamp,
                    author=user[0].id,
                )
            )
    loop.run_until_complete(client.close())
    loop.close()

    CollectionEntry.bulk_create(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("infile")
    parser.add_argument("--key", default="body")
    args = parser.parse_args()

    _main(args)
