from crewai.tools import tool

class ComputerManager:
    def __init__(self):
        self.computers = {}

    def create(self, agent_id: str, **kwargs):
        if agent_id in self.computers:
            return self.computers[agent_id]

        computer = AgentComputer(agent_id, **kwargs)
        self.computers[agent_id] = computer
        return computer

    def get(self, agent_id: str):
        if agent_id not in self.computers:
            raise KeyError(f"No computer assigned to {agent_id}")
        return self.computers[agent_id]


computer_manager = ComputerManager()

@tool("computer_terminal")
def computer_terminal(agent_id: str, command: str) -> str:
    """Execute an authorized shell command in the assigned agent's computer."""
    computer = computer_manager.get(agent_id)

    result = computer.run(command)

    return (
        f"Exit code: {result['exit_code']}\n"
        f"STDOUT:\n{result['stdout']}\n"
        f"STDERR:\n{result['stderr']}"
    )
