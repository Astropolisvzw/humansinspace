import ujson

CONFIG_FILE = 'config.json'

DEFAULT_CONFIG = {
    'update_interval_hours': 6,
    'wifi_networks': []
}

def load_config():
    """Load configuration from file, create default if doesn't exist"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = ujson.load(f)
            print(f"Loaded config: {config}")
            return config
    except:
        print("Config file not found, using defaults")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            ujson.dump(config, f)
        print(f"Saved config: {config}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def add_wifi_network(ssid, password):
    """Add a WiFi network to the configuration"""
    config = load_config()

    # Check if network already exists
    for net in config.get('wifi_networks', []):
        if net['ssid'] == ssid:
            # Update existing network
            net['password'] = password
            save_config(config)
            return True

    # Add new network
    if 'wifi_networks' not in config:
        config['wifi_networks'] = []

    config['wifi_networks'].append({'ssid': ssid, 'password': password})
    return save_config(config)

def remove_wifi_network(ssid):
    """Remove a WiFi network from configuration"""
    config = load_config()

    if 'wifi_networks' in config:
        config['wifi_networks'] = [net for net in config['wifi_networks'] if net['ssid'] != ssid]
        return save_config(config)

    return False

def set_update_interval(hours):
    """Set the update interval in hours"""
    config = load_config()
    config['update_interval_hours'] = hours
    return save_config(config)

def get_wifi_networks():
    """Get list of configured WiFi networks"""
    config = load_config()
    # Also include networks from secrets.py for backward compatibility
    try:
        import secrets
        networks = config.get('wifi_networks', []).copy()

        # Add secrets.py networks if they exist
        if hasattr(secrets, 'WIFI_NETWORKS'):
            for net in secrets.WIFI_NETWORKS:
                # Check if not already in config
                if not any(n['ssid'] == net['ssid'] for n in networks):
                    networks.append(net)

        return networks
    except:
        return config.get('wifi_networks', [])
