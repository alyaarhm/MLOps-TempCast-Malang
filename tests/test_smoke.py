from src.main import load_config

def test_config_loads():
    cfg = load_config()
    assert cfg["project"]["name"] == "TempCast Malang"
    assert cfg["data"]["fetch_frequency"] == "daily"
