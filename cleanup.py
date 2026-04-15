import docker

client = docker.from_env()

def cleanup_old_containers(prefix="web_app_"):
    containers = client.containers.list(all=True)
    removed_any = False

    for c in containers:
        if c.name.startswith(prefix) and c.status != "running":
            c.remove()
            removed_any = True

    return removed_any


def prune_images():
    result = client.images.prune()
    return result.get("ImagesDeleted") is not None


# ---- MAIN LOGIC ----
containers_cleaned = cleanup_old_containers()
images_cleaned = prune_images()

print("Container healthy. Old containers purged")