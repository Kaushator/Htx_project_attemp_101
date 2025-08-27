#!/usr/bin/env python3
import sys
import json
import argparse


def process_message(msg: dict) -> dict:
    payload = msg.get("payload", {})
    return {"type": "response", "payload": payload}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=6000, help="Port for MCP server (informational only)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    if args.debug:
        print("MCP server debug mode", file=sys.stderr)

    # Simple in-process JSON lines protocol over STDIN/STDOUT
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            resp = {"error": "invalid_json", "detail": str(e)}
        else:
            resp = process_message(data)
        print(json.dumps(resp))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
