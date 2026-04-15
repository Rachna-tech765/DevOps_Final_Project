import docker

client = docker.from_env()

def deploy_app(image_name, version):
    print(f"Building image {image_name}:{version}...")
    
    image, build_logs = client.images.build(
        path=".", 
        tag=f"{image_name}:{version}"
    )

    # Remove existing container if exists
    try:
        old_container = client.containers.get(f"web_app_{version}")
        print("Stopping existing container...")
        old_container.stop()
        old_container.remove()
    except:
        pass

    print("Starting container...")
    container = client.containers.run(
        image.id,
        detach=True,
        ports={'5000/tcp': 5000},
        name=f"web_app_{version}"
    )

    print(f"Deployment successful: {container.id}")


deploy_app("healthcare-app", "v1")