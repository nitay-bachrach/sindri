from __future__ import annotations

import argparse
import os
import sys
import typing
import json
import importlib
from urllib.parse import urlsplit

from dns.resolver import Resolver
import yaml

from . import exceptions
from .consts import SINDRI_CONFIG

COMMON_2D_DOMAINS = ["com.", "co.", "org.", "gov.", "net.", "mil."]


def get_main_domain(domain: str) -> str:
    """
    Returns the main domain:
    www.google.com -> google.com
    ir.support.example.co.uk -> example.co.uk
    """
    url_split = urlsplit(domain)
    if not url_split.netloc:
        url_split = urlsplit("http://" + domain)

    domain = url_split.netloc

    if "/" in domain:
        domain = domain[: domain.find("/")]
    l1_domain = ".".join(domain.split(".")[-2:])
    if any(l1_domain.startswith(l2) for l2 in COMMON_2D_DOMAINS):
        l1_domain = ".".join(domain.split(".")[-3:])
    return l1_domain.strip(".")


def get_canonical_name(
    domain: str, nameservers: typing.Optional[list[str]] = None
) -> str:
    _resolver = Resolver()
    _resolver.nameservers = nameservers

    a = _resolver.resolve(domain)
    return b".".join(a.canonical_name.labels).decode().strip(".")


def get_sub_services(
    subdomains: list[str], domain: str, nameservers: typing.Optional[list[str]] = None
) -> dict[str, dict[str, str]]:
    by_service = {}
    for sdomain in subdomains:
        try:
            canon = get_canonical_name(sdomain, nameservers=nameservers)
            if canon == sdomain or canon.endswith(domain):
                continue

            service = get_main_domain(canon)
            if service not in by_service:
                by_service[service] = {}
            by_service[service][sdomain] = canon
        except Exception:
            pass

    return by_service


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("domain")
    parser.add_argument(
        "-n", nargs="*", help="Name servers", default=["8.8.8.8", "1.1.1.1"]
    )
    parser.add_argument("-j", action="store_true", help="JSON Output")
    parser.add_argument("-c", "--config", dest="config", type=argparse.FileType("r"))
    parser.add_argument(
        "--subdomains-output",
        "--so",
        dest="sdomains_out",
        type=argparse.FileType("w"),
        help="Export found subdomains",
    )
    parser.add_argument(
        "--supplier", help="How to list subdomains", default=[], nargs="+"
    )
    args = parser.parse_args()

    if args.config:
        config = yaml.safe_load(args.config)
    elif os.path.exists(os.path.join(SINDRI_CONFIG, "config.yaml")):
        with open(os.path.join(SINDRI_CONFIG, "config.yaml")) as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    subdomains = []
    for supplier in (args.supplier or config.get("suppliers", ["amass"])):
        try:
            module = importlib.import_module(f".supplier_{supplier}", package="sindri")
        except ImportError:
            print(f"Cannot find supplier {supplier}", file=sys.stderr)
            return 0xF0

        if not hasattr(module, "get_subdomains"):
            print(
                f"Supplier {args.supplier} does not export the required function 'get_subdomains'"
            )
            return 0x04

        try:
            subdomains.extend(module.get_subdomains(args.domain, *args.supplier[1:]))

        except exceptions.SindriSupplierNotFound:
            print(f"Cannot load supplier {supplier}", file=sys.stderr)
        except exceptions.SindriSupplierFailedError as e:
            print(f"Supplier failed: {e.args}", file=sys.stderr)

    print(f"{len(subdomains)} domains found")
    if args.sdomains_out:
        args.sdomains_out.write("\n".join(subdomains))

    if config.get("blacklist"):
        # Remove domains with blacklist words, unless it's part of the domain itself
        subdomains = [s for s in subdomains if not any(bl in s.replace(args.domain, "") for bl in config["blacklist"])]
        print(f"Checking {len(subdomains)} domains after filter")

    result = get_sub_services(subdomains, args.domain, args.n)
    if args.j:
        print(json.dumps(result, indent=2))
    else:
        for domain in result:
            print(domain + ":")
            for user_domain, canonical_domain in result[domain].items():
                print(f"    {user_domain} -> {canonical_domain}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
