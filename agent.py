from crewai import Agent, Task, Crew, Process, LLM
from tools import agent_sandbox, RunSandboxCommand

agent_llm = LLM(
    model="ollama/ornith:9b",
    base_url="http://localhost:11434"
    # api_key=os.environ.get("OPENROUTER_API_KEY"),
)

try:
    coding_agent = Agent(
        role="Python Coding Agent",
        goal=(
            "Complete coding tasks by writing code, executing it "
            "inside Docker, checking errors, and fixing problems."
        ),
        backstory=(
            "You are a software engineer. All code execution "
            "must happen using the Docker sandbox tool."
        ),
        tools=[RunSandboxCommand()],
        verbose=True,
        allow_delegation=False,
        llm=agent_llm,
    )

    task = Task(
        description="""
        Create a Python file named hello.py in /workspace.
        The file should print 'Hello from Docker Sandbox!'.

        Execute the file using Python.
        If there are errors, fix them and run it again.
        Report the final output and the commands used.
        """,
        expected_output=(
            "A summary of the created file, execution result, "
            "and any fixes made."
        ),
        agent=coding_agent,
    )

    crew = Crew(
        agents=[coding_agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    print(result)

finally:
    agent_sandbox.close()