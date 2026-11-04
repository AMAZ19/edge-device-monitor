import argparse
import json
import sqlite3

from telemetry_storage import(
        get_latest_telemetry,
        get_temperature_statistics,
)

def build_parser():
        parser = argparse.ArgumentParser(
                description="Query stored IoT telemetry."
        )
        subparsers = parser.add_subparsers(
                dest="command",
                required=True,
        )
        latest_parser = subparsers.add_parser(
                "latest",
                help="Show the latest measurements.",
        )
        latest_parser.add_argument(
                "--limit",
                type=int,
                default=10,
                help="Maximum number of measurements (default: 10).",
        )
        latest_parser.add_argument(
                "--device-id",
                help="Filter by device ID."
        )
        stats_parser = subparsers.add_parser(
                "stats",
                help="Show temperature statistics."
        )
        stats_parser.add_argument(
                "--device-id",
                help="Filter by device ID."
        )
        return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "latest":
            result = get_latest_telemetry(
                limit=args.limit,
                device_id=args.device_id,
            )
        else:
            result = get_temperature_statistics(
                device_id=args.device_id,
            )
    except ValueError as error:
        parser.error(str(error))
    except sqlite3.Error as error:
        parser.exit(
            status=1,
            message=f"Database error: {error}\n",
        )

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
        main()
