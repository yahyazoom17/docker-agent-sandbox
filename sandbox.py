
import docker
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CommandInput(BaseModel):
    command: str = Field(
        description="Shell command to execute in this agent's computer."
    )


class AgentComputer:
    """One persistent Docker computer for one agent."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.client = docker.from_env()

        self.volume = self.client.volumes.create(
            name=f"workspace-{agent_id}"
        )

        self.container = self.client.containers.run(
            image="crewai-agent-computer:latest",
            name=f"computer-{agent_id}",
            command=["sleep", "infinity"],
            detach=True,
            working_dir="/workspace",
            volumes={
                self.volume.name: {
                    "bind": "/workspace",
                    "mode": "rw",
                }
            },
            network_disabled=True,
            mem_limit="1g",
            nano_cpus=1_000_000_000,
            pids_limit=128,
            cap_drop=["ALL"],
            security_opt=["no-new-privileges:true"],
        )

    def execute(self, command: str) -> str:
        # A basic execution-time limit using GNU timeout.
        safe_command = (
            "timeout --signal=TERM --kill-after=2s 30s "
            "bash -lc " + __import__("shlex").quote(command)
        )

        result = self.container.exec_run(
            ["bash", "-lc", safe_command],
            workdir="/workspace",
            demux=True,
        )

        stdout, stderr = result.output

        return (
            f"Exit code: {result.exit_code}\n"
            f"STDOUT:\n{(stdout or b'').decode(errors='replace')}\n"
            f"STDERR:\n{(stderr or b'').decode(errors='replace')}"
        )

    def close(self):
        try:
            self.container.stop(timeout=3)
        finally:
            try:
                self.container.remove(force=True)
            finally:
                self.volume.remove()
                self.client.close()


class ComputerTool(BaseTool):
    name: str = "Computer Terminal"
    description: str = (
        "Use this agent's persistent Linux computer to create files, "
        "run programs, compile code, install or inspect software, "
        "and execute shell commands. The workspace persists between calls."
    )
    args_schema: type[BaseModel] = CommandInput
    computer: AgentComputer

    def _run(self, command: str) -> str:
        return self.computer.execute(command)
