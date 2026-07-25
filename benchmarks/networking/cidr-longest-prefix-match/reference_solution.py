"""Reference implementation of CIDR longest-prefix-match (LPM) routing table
resolution.

See problem.md in this directory for the full contract.
"""
from __future__ import annotations

import ipaddress
from typing import List, Optional, Tuple


def resolve_routes(
    routing_table: List[Tuple[str, str]],
    destinations: List[str],
) -> List[Optional[str]]:
    # Pre-parse the table once, keeping original table order so later
    # duplicate-prefix entries can be preferred (rule 2).
    parsed = [
        (ipaddress.ip_network(cidr, strict=False), next_hop)
        for cidr, next_hop in routing_table
    ]

    results: List[Optional[str]] = []
    for dest in destinations:
        ip = ipaddress.ip_address(dest)

        best_prefixlen = -1
        best_index = -1
        best_hop: Optional[str] = None

        for index, (network, next_hop) in enumerate(parsed):
            if ip.version != network.version:
                continue  # families never intersect
            if ip not in network:
                continue

            prefixlen = network.prefixlen
            # Longest prefix wins; on an exact tie in prefix length AND
            # network (a literal duplicate CIDR), the later table entry
            # wins. Using >= on prefixlen combined with iterating in
            # table order means the last equal-specificity entry for the
            # *same* network naturally overwrites the earlier one, while
            # a later route that is merely equally long but a different
            # (non-containing) network never reaches this branch because
            # `ip not in network` already filtered it out.
            if prefixlen >= best_prefixlen:
                best_prefixlen = prefixlen
                best_index = index
                best_hop = next_hop

        results.append(best_hop if best_index != -1 else None)

    return results
