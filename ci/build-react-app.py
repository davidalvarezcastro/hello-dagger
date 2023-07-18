import sys

import anyio
import dagger

async def main():
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        # node:16-slim container
        source = (
            client.container()
            .from_("node:16-slim")
            .with_directory(
                "/src",
                client.host().directory("."),
                exclude=["node_modules/", "ci/"]
            )
        )

        # dependencies
        runner = source.with_workdir("/src").with_exec(["npm", "install"])

        # tests
        test = runner.with_exec(["npm", "test", "--", "--watchAll=false"])

        # build application
        build_dir = (
            test.with_exec(["npm", "run", "build"])
            .directory("./build")
        )

        await build_dir.export("./build")

        e = await build_dir.entries()

        print(f"build dir contents:\n{e}")

anyio.run(main)