import random
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
                exclude=["node_modules/", "ci/"],
            )
        )

        # dependencies
        runner = source.with_workdir("/src").with_exec(["npm", "install"])

        # tests
        test = runner.with_exec(["npm", "test", "--", "--watchAll=false"])

        # build application
        await (
            test.with_exec(["npm", "run", "build"])
            .directory("./build")
            .export("./build")
        )

        # publish to a nginx:alpine container
        image_ref = await (
            client.container()
            .from_("nginx:1.23-alpine")
            .with_directory("/usr/share/nginx/html", client.host().directory("./build"))
            .publish(f"ttl.sh/hello-dagger-{random.randint(0, 10000000)}")
        )

    print(f"Published image to: {image_ref}")

anyio.run(main)