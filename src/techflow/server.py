"""Development server entrypoint."""

from __future__ import annotations

import argparse
from wsgiref.simple_server import make_server

from .app import TaskManagerApp


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute o TechFlow Task Manager")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--database", default=None)
    args = parser.parse_args()
    app = TaskManagerApp(args.database)
    print(f"TechFlow disponível em http://{args.host}:{args.port}")
    with make_server(args.host, args.port, app) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()

