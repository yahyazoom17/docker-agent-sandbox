
import re
import docker
from docker.errors import NotFound, APIError

class AgentComputer:
    IMAGE = "crewai-code-sandbox:latest"

    def __init__(
        self,
        agent_id: str,
        git_name: str = "agent170207",
        git_email: str = "openaichatgpt839@gmail.com",
    ):
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,47}", agent_id):
            raise ValueError("Invalid agent_id")

        self.agent_id = agent_id
        self.name = f"computer-{agent_id}"
        self.volume_name = f"workspace-{agent_id}"
        self.client = docker.from_env()

        # Ensure the persistent workspace exists.
        self.client.volumes.create(
            name=self.volume_name,
            labels={"managed-by": "crewai", "agent-id": agent_id},
        )

        # Reuse the container if it already exists.
        self.container = self.client.containers.run(
            image="crewai-code-sandbox:latest",
            name=f"computer-{agent_id}",
            command=["sleep", "infinity"],
            detach=True,
            init=True,
            working_dir="/workspace",

            # Root inside the container
            user="0:0",

            volumes={
                f"workspace-{agent_id}": {
                    "bind": "/workspace",
                    "mode": "rw",
                }
            },

            # Resource limits still protect the host
            mem_limit="1g",
            nano_cpus=2_000_000_000,
            pids_limit=256,

            labels={
                "managed-by": "crewai",
                "agent-id": agent_id,
            },
        )
        self.git_name = git_name
        self.git_email = git_email

        self.run("git config --global user.name " + repr(git_name))
        self.run("git config --global user.email " + repr(git_email))

    def run(self, command: str):
        """Run a shell command inside this agent's container."""
        result = self.container.exec_run(
            ["bash", "-lc", command],
            workdir="/workspace",
            user="1000:1000",
            demux=True,
        )

        stdout, stderr = result.output or (None, None)

        return {
            "exit_code": result.exit_code,
            "stdout": (stdout or b"").decode(errors="replace"),
            "stderr": (stderr or b"").decode(errors="replace"),
        }

    def stop(self):
        self.container.stop(timeout=10)

    def start(self):
        self.container.reload()
        if self.container.status != "running":
            self.container.start()

    def close(self):
        """Stop the agent's container without deleting its workspace."""
        try:
            self.container.reload()

            if self.container.status == "running":
                self.container.remove(force=True)

            print(f"Container {self.name} deleted.")
        except docker.errors.NotFound:
            print(f"Container {self.name} no longer exists.")
        
        
    def status(self):
        self.container.reload()
        return self.container.status
