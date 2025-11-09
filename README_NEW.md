client/
│
├── main.py                # Entry point for the Kivy app
├── app.kv                 # Optional KV for global styling
│
├── screens/               # All UI screens
│   ├── __init__.py
│   ├── title_screen.py
│   ├── match_select.py
│   ├── tank_select.py
│   ├── online_setup.py
│   ├── stage1_1.py
│   └── stage1_2.py
│
├── network/               # Networking code for online matches
│   ├── __init__.py
│   └── game_client.py
│
├── utils/                 # Utility code
│   ├── __init__.py
│   └── config.py          # Server port, default constants, etc.
│
└── resource/              # All images, sounds, etc.
    ├── tankImage/
    │   ├── red/
    │   ├── yellow/
    │   ├── green/
    │   └── blue/
    ├── icon.png
    └── other_assets/
