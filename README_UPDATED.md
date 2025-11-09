client/
├── source/
│   ├── main.py
│   ├── screens/
│   │   ├── title_screen.py
│   │   ├── match_select.py
│   │   ├── tank_select.py
│   │   ├── online_setup.py
│   │   ├── stage1_1.py
│   │   └── stage1_2.py
│   ├── network/
│   │   └── game_client.py
│   ├── utils/
│   │   └── config.py
│   └── resource/
│       ├── background.jpg
│       ├── paw.png
│       ├── boom.wav
│       └── tankImage/
│           ├── red/full.png
│           ├── yellow/full.png
│           └── ...
└── buildozer.spec


server/
├─ main.py
├─ network/
│   ├─ game_server.py       # Accept clients, manage rooms
│   └─ network_link.py      # Protocol wrapper for sending/receiving messages
├─ game_logic/
│   ├─ stage1_logic.py      # Stage-specific physics and tank updates
│   └─ game_state.py        # Generic game state management
├─ resource/
│   └─ tank_images/         # Only for server constants or metadata (not full images)
├─ utils/
│   └─ config.py            # Tank speeds, map sizes, bullet speed, etc.
└─ requirements.txt



8️⃣ Deployment Steps on AWS

Build Docker image:

cd server
docker build -t kittykaboom-server .


Run Docker container:

docker run -d -p 5000:5000 kittykaboom-server


Open port 5000 in your AWS security group to allow clients to connect.

Test by connecting your client to:

ws://<AWS_PUBLIC_IP>:5000