"""Deliberately-broken variant of CIDR longest-prefix-match resolution.

Bug (intentional): instead of resolving to the LONGEST-prefix (most
specific) matching route per problem.md rule 1, this returns the FIRST
matching route in `routing_table` order. This is a classic naive-router
bug: it happens to look correct on a routing table with no overlaps, but
gives the wrong next hop whenever a more-specific route is listed after a
less-specific one that also contains the destination (e.g. 10.0.0.0/8
listed before 10.1.0.0/16 — a destination of 10.1.2.3 should resolve via
the /16, but this implementation stops at the first match, the /8).
"""
from __future__ import annotations

import ipaddress
from typing import List, Optional, Tuple


def resolve_routes(
    routing_table: List[Tuple[str, str]],
    destinations: List[str],
) -> List[Optional[str]]:
    parsed = [
        (ipaddress.ip_network(cidr, strict=False), next_hop)
        for cidr, next_hop in routing_table
    ]

    results: List[Optional[str]] = []
    for dest in destinations:
        ip = ipaddress.ip_address(dest)

        matched_hop: Optional[str] = None
        for network, next_hop in parsed:
            if ip.version != network.version:
                continue
            if ip in network:
                # BUG: takes the first match instead of the longest
                # (most-specific) prefix among all matches.
                matched_hop = next_hop
                break

        results.append(matched_hop)

    return results
