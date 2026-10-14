from crewai import Agent, Task, Crew, Process, LLM
import os
from crewai.tools import tool
from sandbox import AgentComputer
from dotenv import load_dotenv

#* Load environment variables from .env file
load_dotenv()

#* 0. Initialize the LLM with OpenRouter
openrouter_llm = LLM(
    model="openrouter/cohere/north-mini-code:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

#* 1. Create an isolated computer for each agent
computer_1 = AgentComputer(agent_id="coding-agent-1")
computer_2 = AgentComputer(agent_id="coding-agent-2")


#* 2. Create a terminal tool bound to a specific computer
def make_terminal_tool(computer, tool_name):

    @tool(tool_name)
    def computer_terminal(command: str) -> str:
        """Execute a shell command inside your assigned Docker computer.
        Use this tool for creating files, running code, and debugging.
        All code execution must happen inside this Docker computer.
        """
        result = computer.run(command)

        return (
            f"Exit code: {result['exit_code']}\n"
            f"STDOUT:\n{result['stdout']}\n"
            f"STDERR:\n{result['stderr']}"
        )

    return computer_terminal


terminal_tool_1 = make_terminal_tool(
    computer_1, "agent_1_docker_terminal"
)

terminal_tool_2 = make_terminal_tool(
    computer_2, "agent_2_docker_terminal"
)



#* 3. Create agents with their own tools
coding_agent = Agent(
    role="Python Coding Agent 1",
    goal=(
        "Complete coding tasks by writing code, executing it "
        "inside your assigned Docker computer, checking errors, "
        "and fixing problems."
    ),
    backstory=(
        "You are a software engineer with your own isolated Docker "
        "computer. Use only your assigned Docker terminal for code "
        "execution. Never claim success without checking the output."
    ),
    tools=[terminal_tool_1],
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm,
)

coding_agent_2 = Agent(
    role="Python Coding Agent 2",
    goal=(
        "Complete coding tasks by writing code, executing it "
        "inside your assigned Docker computer, checking errors, "
        "and fixing problems."
    ),
    backstory=(
        "You are a software engineer with your own isolated Docker "
        "computer. Use only your assigned Docker terminal for code "
        "execution. Never claim success without checking the output."
    ),
    tools=[terminal_tool_2],
    verbose=True,
    allow_delegation=False,
    llm=openrouter_llm,
)



#* 4. Define tasks
task_1 = Task(
    description="""
    In your assigned Docker computer, create /workspace/hello.py.

    The file must print:
    Hello from Docker Sandbox 1!

    Execute it using Python. If an error occurs, inspect the error,
    fix the file, and execute it again.

    Report the commands used, final output, and file path.
    Do not claim success without verifying the execution output.
    """,
    expected_output=(
        "Created file path, commands used, verified execution output, "
        "and any fixes made."
    ),
    agent=coding_agent,
)

task_2 = Task(
    description="""
    In your assigned Docker computer, create /workspace/hello2.py.

    The file must print:
    Hello from Docker Sandbox 2!

    Execute it using Python. If an error occurs, inspect the error,
    fix the file, and execute it again.

    Report the commands used, final output, and file path.
    Do not claim success without verifying the execution output.
    """,
    expected_output=(
        "Created file path, commands used, verified execution output, "
        "and any fixes made."
    ),
    agent=coding_agent_2,
)



#* 5. Run the tasks
crew = Crew(
    agents=[coding_agent, coding_agent_2],
    tasks=[task_1, task_2],
    process=Process.sequential,
    verbose=True,
)

try:
    result = crew.kickoff()
    print(result)
finally:
    #* Stop the agents' containers after the tasks are complete
    computer_1.close()
    computer_2.close()
