from dotenv import load_dotenv
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from sandbox import DockerSandbox

load_dotenv()

agent_sandbox = DockerSandbox()

class RunCommandInput(BaseModel):
    command: str = Field(
        ...,
        description=(
            "A shell command to execute in the isolated "
            "Docker workspace. Use /workspace for files."
        ),
    )

class RunSandboxCommand(BaseTool):
    name: str = "Run Docker Sandbox Command"
    description: str = (
        "Execute a shell command inside an isolated Docker "
        "container. Use it to create files, run Python code, "
        "and execute tests. Returns stdout, stderr, and exit code."
    )
    args_schema: type[BaseModel] = RunCommandInput

    def _run(self, command: str) -> str:
        return agent_sandbox.run(command)