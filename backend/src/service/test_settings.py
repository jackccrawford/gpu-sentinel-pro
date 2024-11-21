from settings import settings

def test_config():
    print("Testing configuration loading...")
    
    # Test basic config access
    base_interval = settings.get('polling', 'base_interval')
    print(f"Base polling interval: {base_interval}")
    
    # Test nested config access
    low_threshold = settings.get('polling', 'activity_thresholds', 'low', 'interval')
    print(f"Low activity polling interval: {low_threshold}")
    
    # Test default values
    unknown = settings.get('unknown', 'key', default='default_value')
    print(f"Unknown key with default: {unknown}")

if __name__ == "__main__":
    test_config()
