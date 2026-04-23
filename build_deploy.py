import docker
import time
import requests
import logging

# 1. SETUP LOGGING (Ma'am's 1st point)
logging.basicConfig(filename='deployment.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

client = docker.from_env()

def deploy_with_health_check(image_name, version):
    full_image_tag = f"{image_name}:{version}"
    
    try:
        logging.info(f"Deployment started for version: {version}")
        print(f"--- Deploying {full_image_tag} ---")

        # 2. MULTI-VERSION BUILD (Ma'am's 3rd point)
        print("Building image...")
        client.images.build(path=".", tag=full_image_tag)
        logging.info(f"Image {full_image_tag} built successfully.")

        # Cleanup old container
        try:
            old_container = client.containers.get("cyber_app_container")
            old_container.stop()
            old_container.remove()
            logging.info("Old container stopped and removed.")
        except:
            pass

        # Start new container
        container = client.containers.run(
            full_image_tag,
            detach=True,
            ports={'5050/tcp': 5050},
            name="cyber_app_container"
        )
        
        # 3. HEALTH CHECK (Ma'am's 2nd point)
        print("Running Health Check...")
        time.sleep(5) # Wait for app to start
        try:
            response = requests.get("http://localhost:5050")
            if response.status_code == 200:
                print("✅ Health Check Passed! App is live.")
                logging.info("Health Check Passed.")
            else:
                print("❌ Health Check Failed! Status Code:", response.status_code)
                logging.error(f"Health Check Failed with status {response.status_code}")
        except Exception as e:
            print("❌ Health Check Failed! App not reachable.")
            logging.error(f"Health Check Exception: {str(e)}")

    except Exception as e:
        logging.error(f"Deployment crashed: {str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ma'am can change version here easily
    deploy_with_health_check("cyber-app", "v2.0")