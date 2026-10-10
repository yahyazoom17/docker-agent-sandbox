
import docker
from docker.errors import DockerException

class DockerSandbox:
    def __init__(self, image="crewai-code-sandbox"):
        self.client = docker.from_env()
        self.container = self.client.containers.run(
            image=image,
            command=["sleep", "infinity"],
            detach=True,
            working_dir="/workspace",
            remove=True,
            stdout=True,
            stderr=True,
            network_disabled=False,
            network_mode="bridge",
            mem_limit="128m",
            nano_cpus=500_000_000,
            pids_limit=64,
        )

    def run(self, command: str) -> str:
        result = self.container.exec_run(
            ["bash", "-lc", command],
            workdir="/workspace",
            demux=True,
        )

        exit_code = result.exit_code
        stdout, stderr = result.output

        output = (stdout or b"").decode(errors="replace")
        errors = (stderr or b"").decode(errors="replace")

        return (
            f"Exit code: {exit_code}\n"
            f"STDOUT:\n{output}\n"
            f"STDERR:\n{errors}"
        )

    def close(self):
        try:
            self.container.remove(force=True)
        except docker.errors.NotFound:
            pass

        self.client.close()
