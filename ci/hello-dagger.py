import sys

import anyio
import dagger


async def main():
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        python = (
            client.container().from_("python:3.11-slim").with_exec(["python", "-V"])
        )
        version = await python.stdout()

    print(f"Hello from Dagger and {version}")

anyio.run(main)
