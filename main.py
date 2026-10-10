import docker

client = docker.from_env()

print("Docker daemon is running:", client.ping())
print("Container list:")
for container in client.containers.list():
    print(f" - {container.name}")