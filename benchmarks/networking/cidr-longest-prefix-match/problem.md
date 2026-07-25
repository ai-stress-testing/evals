# CIDR Longest-Prefix-Match Routing

## Niche

Implement the core lookup function of an IP router's **forwarding table**:
**longest-prefix match (LPM)**. A router holds a routing table of CIDR
blocks, each mapped to a next-hop. When a packet destined for some IP
address arrives, the router must resolve it to the single **most specific**
(longest prefix length / smallest block) matching route — the same
algorithm real routers, `ip route`, and BGP RIB/FIB lookups use. This is a
routing-table lookup problem, not a generic string/interval puzzle:
overlapping CIDR blocks are expected and must be disambiguated purely by
prefix length, with ties broken deterministically.

## Required interface

Your solution file must define, at module scope, exactly this function:

```python
def resolve_routes(
    routing_table: list[tuple[str, str]],
    destinations: list[str],
) -> list[str | None]:
    """
    routing_table: a list of (cidr, next_hop) pairs, e.g.
        [("10.0.0.0/8", "hop-A"), ("10.1.0.0/16", "hop-B")]
        `cidr` is a string in standard CIDR notation (IPv4 or IPv6, e.g.
        "192.168.1.0/24", "::/0"). `next_hop` is an opaque non-empty string
        identifier (a hostname, interface name, or router ID — never
        interpreted, only returned verbatim).

    destinations: a list of plain IP address strings (IPv4 or IPv6,
        e.g. "10.1.2.3", "::1") to resolve, in the given order.

    Returns: a list the same length and order as `destinations`. For each
    destination IP, the corresponding output element is the next_hop string
    of the routing_table entry whose CIDR block:
      1. contains that IP, AND
      2. among all containing blocks, has the LONGEST prefix length
         (the most specific match — standard longest-prefix-match
         semantics).
    If no routing_table entry contains the destination IP, the
    corresponding output element is None (i.e. "no route").
    """
```

## Behavior contract

1. **Longest prefix wins.** If two or more CIDR blocks contain the
   destination IP, the block with the greater prefix length (e.g. `/24`
   beats `/8`) is the match — regardless of the order the routes appear
   in `routing_table`.
2. **Exact tie on prefix length is a table-order tiebreak.** If two
   routing-table entries have the identical CIDR block (same network
   address AND same prefix length) — a duplicate/overwritten route — the
   entry that appears **later** in `routing_table` wins (mirrors a router
   accepting the most-recently-installed route for an identical prefix).
   Two *different* networks that happen to share a prefix length (e.g.
   `10.0.0.0/24` and `192.168.1.0/24`) are not a tie in this sense — each
   only matches IPs within its own block, so this rule only fires for
   literal duplicate CIDRs.
3. **No matching route → `None`** for that destination. Do not raise, do
   not skip the output slot — the returned list must always be the same
   length as `destinations`.
4. **Mixed address families**: the routing table and destination list may
   mix IPv4 and IPv6 entries. An IPv4 destination must never match an
   IPv6 CIDR block and vice versa, even where a naive integer/string
   comparison might collide.
5. **Boundary addresses**: the network address itself and the broadcast/
   last address of a block are both "inside" the block and must match
   (e.g. `10.0.0.0` and `10.0.0.255` both match `10.0.0.0/24`).
6. **`/32` (IPv4) and `/128` (IPv6) host routes** match only that single
   exact address.
7. **`/0` default route** (e.g. `"0.0.0.0/0"` or `"::/0"`) matches every
   address of that family and must only win when nothing more specific
   matches (per rule 1, its prefix length of 0 is the smallest, so any
   other match takes priority).
8. Input IPs and CIDRs are always well-formed (no need to validate/reject
   malformed input); focus on correct LPM resolution semantics.

## Edge cases to handle

- Overlapping blocks of different specificity, e.g. table contains both
  `10.0.0.0/8` and `10.1.0.0/16`; a destination of `10.1.2.3` must
  resolve to the `/16` route's next hop, not the `/8`'s.
- A destination that matches no block at all → `None`.
- A destination that lands exactly on a block's network address or its
  last address (subnet boundary).
- A duplicate CIDR string appearing twice in `routing_table` with two
  different next hops → the later entry's next hop wins.
- An IPv4-mapped-looking address must not spuriously match an IPv6 block
  or vice versa — the two address families never intersect.
- An empty `routing_table` (every destination resolves to `None`) and an
  empty `destinations` list (returns `[]`).
