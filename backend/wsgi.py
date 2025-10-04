import os
from . import create_app, socketio

# Create app with production config
app = create_app(config_name="production")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)


