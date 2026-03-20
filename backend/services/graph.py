import logging
from typing import Dict
from ..internal_types import GraphResponse, GraphNode, GraphEdge
from ..config import MIXER_ADDRESSES
from .blockchain import fetch_chain_history

logger = logging.getLogger(__name__)

def build_graph_data(target_address: str, chain: str = "ETH") -> GraphResponse:
    target_address = target_address.lower()
    nodes: Dict[str, GraphNode] = {}
    edges = []
    
    def add_node(addr, label, n_type, val=0.0):
        addr = addr.lower()
        if addr not in nodes:
            nodes[addr] = GraphNode(id=addr, label=label, type=n_type, value=val)
        else:
            nodes[addr].value += val

    def add_edge(src, dst, val):
        src, dst = src.lower(), dst.lower()
        existing = next((e for e in edges if e.source == src and e.target == dst), None)
        if existing:
            existing.value += val
            existing.interaction_count += 1
        else:
            edges.append(GraphEdge(source=src, target=dst, value=val, interaction_count=1))

    add_node(target_address, "TARGET", "target")

    level1_txs = fetch_chain_history(target_address, chain)

    partner_agg: Dict[str, dict] = {}

    print(f"Analyzing {len(level1_txs)} L1 transactions (capped at top 50 partners)...")

    for tx in level1_txs:
        try:
            val = float(tx.get("value", 0)) / 10**18
            frm = tx.get("from", "").lower()
            to  = tx.get("to",   "").lower()

            if frm == target_address:
                partner   = to
                direction = "OUT"
            else:
                partner   = frm
                direction = "IN"

            if not partner or partner == target_address:
                continue

            n_type = "mixer" if partner in MIXER_ADDRESSES else "partner"
            label  = "MIXER!" if n_type == "mixer" else partner[:6] + "..."

            if partner not in partner_agg:
                partner_agg[partner] = {"value": 0.0, "direction": direction,
                                        "n_type": n_type, "label": label}
            partner_agg[partner]["value"] += val
            
            if partner_agg[partner]["direction"] != direction:
                partner_agg[partner]["direction"] = "BOTH"

        except (ValueError, KeyError, IndexError) as e:
            logger.debug(f"Skipping malformed L1 transaction: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error processing L1 transaction: {e}")

    MAX_GRAPH_PARTNERS = 50
    top_partners = sorted(partner_agg.items(), key=lambda x: x[1]["value"], reverse=True)[:MAX_GRAPH_PARTNERS]

    partners: Dict[str, float] = {}
    for partner, info in top_partners:
        add_node(partner, info["label"], info["n_type"], info["value"])
        direction = info["direction"]
        if direction in ("OUT", "BOTH"):
            add_edge(target_address, partner, info["value"])
        else:
            add_edge(partner, target_address, info["value"])
        if info["n_type"] != "mixer":
            partners[partner] = info["value"]

    sorted_partners = sorted(partners.items(), key=lambda x: x[1], reverse=True)[:2]
    
    print(f"Deep Tracing Top Partners: {[p[0] for p in sorted_partners]}")

    for partner_addr, _ in sorted_partners:
        if partner_addr in MIXER_ADDRESSES:
            continue
        
        l2_txs = fetch_chain_history(partner_addr, chain)
        
        for tx in l2_txs[:10]:
            try:
                val = float(tx.get("value", 0)) / 10**18
                frm = tx.get("from", "").lower()
                to = tx.get("to", "").lower()
                
                other = to if frm == partner_addr else frm
                if not other:
                    continue

                is_mixer = other in MIXER_ADDRESSES
                is_high_val = val > 1.0 
                is_existing = other in nodes

                if is_mixer or is_existing or is_high_val:
                    n_type = "partner_l2"
                    label = other[:6]
                    if is_mixer: 
                        n_type = "mixer"
                        label = "MIXER!"
                    
                    add_node(other, label, n_type, val)
                    
                    if frm == partner_addr:
                        add_edge(partner_addr, other, val)
                    else:
                        add_edge(other, partner_addr, val)
            except (ValueError, KeyError, IndexError) as e:
                logger.debug(f"Skipping malformed L2 transaction: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error processing L2 transaction: {e}")
                continue

    return GraphResponse(nodes=list(nodes.values()), edges=edges)