import os
import socket

from app import create_app


def _port_is_available(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("127.0.0.1", port))
    except OSError:
        return False
    finally:
        sock.close()
    return True


def _resolve_port() -> int:
    # If user explicitly sets PORT, respect it.
    env_port = os.environ.get("PORT")
    if env_port:
        try:
            return int(env_port)
        except ValueError as exc:
            raise RuntimeError("PORT must be an integer.") from exc

    default_port = 5000
    fallback_port = 5050
    if _port_is_available(default_port):
        return default_port
    return fallback_port


app = create_app()

if __name__ == "__main__":
    port = _resolve_port()
    if port != 5000:
        print("Port 5000 is in use. Starting on port 5050 instead.")
    app.run(debug=True, port=port)
