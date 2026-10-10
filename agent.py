from crewai import Agent, Task, Crew, Process, LLM
from sandbox import AgentComputer, ComputerTool
import os

agent_llm = LLM(
    model="openrouter/poolside/laguna-xs-2.1:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

backend_pc = AgentComputer("backend")
frontend_pc = AgentComputer("frontend")

backend = Agent(
    role="Backend Developer",
    goal="Build and test the backend independently",
    backstory="You are a developer with your own Linux computer.",
    tools=[ComputerTool(computer=backend_pc)],
    verbose=True,
    llm=agent_llm
)

frontend = Agent(
    role="Frontend Developer",
    goal="Build and test the frontend independently",
    backstory="You are a frontend developer with your own Linux computer.",
    tools=[ComputerTool(computer=frontend_pc)],
    verbose=True,
    llm=agent_llm
)

tasks = [
    Task(
        description=(
            "Create and test a small Python fastapi backend in your "
            "own /workspace directory. Report the files created and the test results. Give me the link to the working backend after testing it."
        ),
        expected_output="Working backend source and test results.",
        agent=backend,
    ),
    Task(
        description=(
            "Create a simple react frontend"
            "in your own /workspace directory. Report the files created."
            "after testing the frontend, give me the link to the working frontend."
        ),
        expected_output="Working frontend source files.",
        agent=frontend,
    ),
]

try:
    crew = Crew(
        agents=[backend, frontend],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    print(result)
finally:
    backend_pc.close()
    frontend_pc.close()
