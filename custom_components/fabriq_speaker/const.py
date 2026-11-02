"""Constants for the Fabriq Wi-Fi Speaker integration."""

DOMAIN = "fabriq_speaker"

CONF_HOST = "host"
CONF_NAME = "name"

DEFAULT_PORT = 80
SCAN_INTERVAL_SECONDS = 10

EQ_MODES = {
    "0": "Normal (Flat)",
    "1": "Klasik (Classic)",
    "2": "Pop",
    "3": "Bass / Jazz",
    "4": "Vokal (Vocal)",
}
EQ_MODE_TO_CODE = {v: k for k, v in EQ_MODES.items()}

INPUT_SOURCES = {
    "wifi": "Wi-Fi / Ağ",
    "bluetooth": "Bluetooth",
    "line-in": "AUX (Line-In)",
}
SOURCE_TO_CMD = {v: k for k, v in INPUT_SOURCES.items()}

PLAYER_MODE_MAP = {
    "0": "Wi-Fi / Ağ",
    "10": "Wi-Fi / Ağ",
    "1": "AirPlay",
    "2": "DLNA",
    "31": "Spotify Connect",
    "40": "AUX (Line-In)",
    "41": "Bluetooth",
    "43": "Optik",
    "99": "Multiroom Slave",
}

CHANNEL_MODES = {
    "0": "Stereo (L+R)",
    "1": "Sol Kanal (Left)",
    "2": "Sağ Kanal (Right)",
}
CHANNEL_TO_CODE = {v: k for k, v in CHANNEL_MODES.items()}
