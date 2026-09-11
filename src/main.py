import yaml

def load_config(path="config/config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    cfg = load_config()
    print(f"Project: {cfg['project']['name']}")
    print(f"Task   : {cfg['project']['task']}")
    print(f"Source : {cfg['data']['source']}")
    print("TempCast Malang development environment is ready.")
