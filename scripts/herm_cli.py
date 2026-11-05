"""
Script: scripts/herm_cli.py
Interactive Command-Line Interface (CLI) and REPL for HERM4AI.
Allows users and researchers to query, inspect, link, decay, and audit memories interactively.
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Ensure project root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.herm4ai.models import Assertion
from src.herm4ai.engine import HERMMemoryEngine
from src.herm4ai.observability import render_provenance_timeline


DB_FILE = "herm_local_store.db"


def get_engine():
    return HERMMemoryEngine(DB_FILE)


def cmd_insert(args):
    eng = get_engine()
    a = Assertion(
        entity=args.entity,
        attribute=args.attribute,
        value=args.value,
        timestamp=datetime.now().isoformat(),
        source=args.source or "CLI_User"
    )
    eng.ingest([a])
    print(f"[+] Successfully inserted: {args.entity}.{args.attribute} = '{args.value}' (Source: {a.source})")


def cmd_query(args):
    eng = get_engine()
    now_iso = datetime.now().isoformat()
    res = eng.query(args.entity, args.attribute, "CLI Query", now_iso)
    print(render_provenance_timeline(res))
    if res.associative_context:
        print("\n--- Associative Connections (1-Hop) ---")
        for edge in res.associative_context:
            target = edge["target_entity"] if edge["source_entity"] == args.entity else edge["source_entity"]
            print(f"  --> [{edge['relation']}] {target} (weight: {edge['weight']})")


def cmd_relate(args):
    eng = get_engine()
    edge = eng.relate(
        source_entity=args.source_entity,
        relation=args.relation,
        target_entity=args.target_entity,
        weight=args.weight,
        source="CLI_User"
    )
    print(f"[+] Created Associative Edge: {edge.source_entity} --[{edge.relation}]--> {edge.target_entity} (weight={edge.weight})")


def cmd_spread(args):
    eng = get_engine()
    scores = eng.associative_spread(args.entity, max_hops=args.hops)
    print(f"\n=== SPREADING ACTIVATION FROM: {args.entity} ===")
    for ent, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        bar = "#" * int(score * 20)
        print(f"  {ent:<30} : {score:0.4f}  |{bar:<20}|")


def cmd_impact(args):
    eng = get_engine()
    impact = eng.impact_analysis(args.entity)
    print(f"\n=== DEPENDENCY IMPACT ANALYSIS FOR: {args.entity} ===")
    print(f"Total Associated Nodes: {impact['dependency_count']}")
    for dep in impact["dependencies"]:
        print(f"  [{dep['direction'].upper()}] --({dep['relation']})--> {dep['entity']} (weight={dep['weight']})")


def cmd_delete(args):
    eng = get_engine()
    a = Assertion(
        entity=args.entity,
        attribute=args.attribute,
        value=None,
        timestamp=datetime.now().isoformat(),
        source=args.source or "CLI_Purge_Request",
        is_deletion=True
    )
    eng.ingest([a])
    print(f"[-] Successfully expunged: {args.entity}.{args.attribute} under tombstone deletion.")


def cmd_decay(args):
    eng = get_engine()
    future_time = (datetime.now() + timedelta(days=args.days)).isoformat()
    report = eng.apply_temporal_decay(future_time, archive_threshold=args.threshold)
    print(f"\n=== COGNITIVE TEMPORAL DECAY SIMULATION ===")
    print(f"Simulated Time      : {future_time} (+{args.days} days)")
    print(f"Memories Evaluated  : {report['memories_evaluated']}")
    print(f"Memories Archived   : {report['memories_archived']} (threshold: {report['archive_threshold']})")


def cmd_stats(args):
    eng = get_engine()
    cursor = eng.conn.cursor()
    cursor.execute("SELECT count(*) FROM memories")
    n_mem = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM memories WHERE status = 'ACTIVE'")
    n_act = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM memories WHERE status = 'SUPERSEDED'")
    n_sup = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM memories WHERE status = 'CONFLICTED'")
    n_cnf = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM memories WHERE status = 'ARCHIVED'")
    n_arc = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM associative_edges")
    n_edges = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM procedural_routines")
    n_proc = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM provenance_log")
    n_prov = cursor.fetchone()[0]

    db_size = os.path.getsize(DB_FILE) / 1024.0 if os.path.exists(DB_FILE) else 0.0

    print("\n==================================================")
    print(" HERM4AI COGNITIVE STORE SUMMARY STATISTICS")
    print("==================================================")
    print(f" Local Storage File       : {DB_FILE} ({db_size:.1f} KB)")
    print(f" Total Memories Stored    : {n_mem}")
    print(f"   - Active Facts         : {n_act}")
    print(f"   - Superseded History   : {n_sup}")
    print(f"   - Conflicted Claims    : {n_cnf}")
    print(f"   - Archived / Dormant   : {n_arc}")
    print(f" Associative Graph Edges  : {n_edges}")
    print(f" Procedural Routines      : {n_proc}")
    print(f" Immutable Provenance Logs: {n_prov}")
    print("==================================================")


def main():
    parser = argparse.ArgumentParser(description="HERM4AI Cognitive Memory CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # insert
    p_ins = subparsers.add_parser("insert", help="Insert or update a factual memory")
    p_ins.add_argument("entity", help="Entity name")
    p_ins.add_argument("attribute", help="Attribute name")
    p_ins.add_argument("value", help="Value")
    p_ins.add_argument("--source", default="CLI_User", help="Source provenance")
    p_ins.set_defaults(func=cmd_insert)

    # query
    p_qry = subparsers.add_parser("query", help="Query a memory with full provenance")
    p_qry.add_argument("entity", help="Entity name")
    p_qry.add_argument("attribute", help="Attribute name")
    p_qry.set_defaults(func=cmd_query)

    # relate
    p_rel = subparsers.add_parser("relate", help="Create an associative edge between entities")
    p_rel.add_argument("source_entity", help="Source entity")
    p_rel.add_argument("relation", help="Relation type (e.g. LEADS, DEPENDS_ON)")
    p_rel.add_argument("target_entity", help="Target entity")
    p_rel.add_argument("--weight", type=float, default=1.0, help="Association weight (0.0-1.0)")
    p_rel.set_defaults(func=cmd_relate)

    # spread
    p_spd = subparsers.add_parser("spread", help="Run spreading activation across the associative graph")
    p_spd.add_argument("entity", help="Starting entity")
    p_spd.add_argument("--hops", type=int, default=2, help="Maximum traversal hops")
    p_spd.set_defaults(func=cmd_spread)

    # impact
    p_imp = subparsers.add_parser("impact", help="Analyze downstream dependency impact of an entity")
    p_imp.add_argument("entity", help="Target entity")
    p_imp.set_defaults(func=cmd_impact)

    # delete
    p_del = subparsers.add_parser("delete", help="Expunge a memory under tombstone request")
    p_del.add_argument("entity", help="Entity name")
    p_del.add_argument("attribute", help="Attribute name")
    p_del.add_argument("--source", default="CLI_Purge", help="Purge requester")
    p_del.set_defaults(func=cmd_delete)

    # decay
    p_dcy = subparsers.add_parser("decay", help="Simulate temporal forgetting and decay")
    p_dcy.add_argument("--days", type=int, default=30, help="Elapsed days to simulate")
    p_dcy.add_argument("--threshold", type=float, default=0.15, help="Archiving threshold")
    p_dcy.set_defaults(func=cmd_decay)

    # stats
    p_sta = subparsers.add_parser("stats", help="Display store summary statistics")
    p_sta.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
