"""Monitor expiration of MQTT TLS certificates."""

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def get_certificate_expiry(cert_path):
    """Return the certificate expiration date in UTC."""
    path = Path(cert_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Certificate not found: {cert_path}"
        )

    result = subprocess.run(
        ["openssl", "x509", "-in", str(path), "-noout", "-enddate"],
        capture_output=True,
        text=True,
        check=True,
    )

    expiry = result.stdout.strip().removeprefix("notAfter=")

    return datetime.strptime(
        expiry, "%b %d %H:%M:%S %Y %Z"
    ).replace(tzinfo=timezone.utc)


def check_certificate(cert_path, warning_days=30):
    """Return certificate status and remaining days."""
    if warning_days < 0:
        raise ValueError("warning_days must not be negative")

    expiry = get_certificate_expiry(cert_path)
    remaining = expiry - datetime.now(timezone.utc)
    days = remaining.total_seconds() / 86400

    if days <= 0:
        status = "EXPIRED"
    elif days <= warning_days:
        status = "WARNING"
    else:
        status = "OK"

    return status, days, expiry


def main():
    parser = argparse.ArgumentParser(
        description="Check MQTT TLS certificate expiration"
    )

    parser.add_argument(
        "certificates",
        nargs="+",
        help="Certificate files to check",
    )

    parser.add_argument(
        "--warning-days",
        type=int,
        default=30,
    )

    args = parser.parse_args()
    exit_code = 0

    for cert_path in args.certificates:
        try:
            status, days, expiry = check_certificate(
                cert_path,
                args.warning_days,
            )

            print(
                f"{cert_path}: {status} | "
                f"{days:.1f} days remaining | "
                f"Expires: {expiry.isoformat()}"
            )

            if status != "OK":
                exit_code = 1

        except (OSError, ValueError, KeyError) as exc:
            print(f"{cert_path}: ERROR | {exc}")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
