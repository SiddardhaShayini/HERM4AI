"""
Script: scripts/generate_benchmark_data.py
Generates the synthetic TFSR-Bench (Temporal Fact & State Revision) datasets:
1. data/pilot_dataset.json (30 cases, for preliminary tuning & boundary checking)
2. data/heldout_dataset.json (60 cases, held-out evaluation set)

All generation is deterministic using a fixed random seed.
"""

import json
import random
from pathlib import Path


def generate_benchmark_splits(seed: int = 42):
    random.seed(seed)

    entities = [
        "Dr. Aris Thorne", "Dr. Elena Rostova", "Marcus Vance", "Sora Takahashi",
        "Amina Diallo", "Chen Wei", "Carlos Mendez", "Ingrid Lindholm",
        "Devin Brooks", "Fatima Al-Zahra", "Liam O'Connor", "Priya Sharma",
        "Project-Vanguard", "Project-Chimera", "Database-Cluster-9", "Core-Router-B",
        "Auth-Service-V2", "Quantum-Lab-Subnet", "Satellite-Orion-4", "Fleet-Vehicle-108"
    ]

    attributes = [
        "primary_residence", "security_clearance", "active_project", "employment_status",
        "hardware_status", "operating_frequency", "encryption_protocol", "current_role"
    ]

    values_pool = {
        "primary_residence": ["Zurich", "Tokyo", "Berlin", "Nairobi", "Toronto", "Singapore", "Sao Paulo", "Reykjavik"],
        "security_clearance": ["Level-1", "Level-2", "Level-3", "Top-Secret", "Restricted", "Public-Trust"],
        "active_project": ["Neural-Core", "Project-Genesis", "Deep-Memory", "Atlas-X", "Helios-9", "Titan-V"],
        "employment_status": ["Full-Time", "Contractor", "On-Leave", "Sabbatical", "Senior-Fellow"],
        "hardware_status": ["Operational", "Degraded", "Under-Maintenance", "Decommissioned", "Standby"],
        "operating_frequency": ["2.4 GHz", "5.8 GHz", "60 GHz", "10.5 GHz", "14.2 GHz"],
        "encryption_protocol": ["TLS-1.3", "AES-256-GCM", "ChaCha20-Poly1305", "Post-Quantum-Kyber"],
        "current_role": ["Lead Architect", "Principal Scientist", "Director of Research", "Security Auditor"]
    }

    sources_pool = ["HR_Database", "Directory_Service", "Device_Telemetry", "Audit_Log", "Project_Registry"]

    def create_case(case_id: str, category: str, split_name: str) -> dict:
        entity = random.choice(entities)
        attr = random.choice(attributes)
        v_pool = values_pool[attr]
        source = random.choice(sources_pool)

        if category == "DR":
            # Direct Recall: fact asserted once, then multiple distractors
            val = random.choice(v_pool)
            assertions = [
                {
                    "entity": entity,
                    "attribute": attr,
                    "value": val,
                    "timestamp": "2024-01-15T09:00:00Z",
                    "source": source,
                    "confidence": 0.95,
                    "is_deletion": False
                }
            ]
            # Add 2 distractor assertions for other entities/attributes
            for _ in range(2):
                other_e = random.choice([e for e in entities if e != entity])
                other_attr = random.choice(attributes)
                assertions.append({
                    "entity": other_e,
                    "attribute": other_attr,
                    "value": random.choice(values_pool[other_attr]),
                    "timestamp": "2024-02-01T12:00:00Z",
                    "source": random.choice(sources_pool),
                    "confidence": 0.90,
                    "is_deletion": False
                })
            random.shuffle(assertions)

            return {
                "id": case_id,
                "split": split_name,
                "category": "DR",
                "assertions": assertions,
                "query": {
                    "entity": entity,
                    "attribute": attr,
                    "query_text": f"What is the {attr.replace('_', ' ')} of {entity}?",
                    "query_time": "2024-06-01T00:00:00Z"
                },
                "ground_truth": {
                    "expected_value": val,
                    "expected_status": "ACTIVE"
                }
            }

        elif category == "TR":
            # Temporal Revision: original fact at t1, revised fact at t2 > t1
            sample_vals = random.sample(v_pool, 2)
            val_old, val_new = sample_vals[0], sample_vals[1]

            assertions = [
                {
                    "entity": entity,
                    "attribute": attr,
                    "value": val_old,
                    "timestamp": "2024-01-10T10:00:00Z",
                    "source": source,
                    "confidence": 0.90,
                    "is_deletion": False
                },
                {
                    "entity": entity,
                    "attribute": attr,
                    "value": val_new,
                    "timestamp": "2024-05-20T14:30:00Z",
                    "source": source,
                    "confidence": 0.95,
                    "is_deletion": False
                }
            ]

            return {
                "id": case_id,
                "split": split_name,
                "category": "TR",
                "assertions": assertions,
                "query": {
                    "entity": entity,
                    "attribute": attr,
                    "query_text": f"What is the current {attr.replace('_', ' ')} of {entity}?",
                    "query_time": "2024-06-01T00:00:00Z"
                },
                "ground_truth": {
                    "expected_value": val_new,
                    "expected_status": "ACTIVE",
                    "superseded_value": val_old
                }
            }

        elif category == "CA":
            # Conflict Attribution: Source A and Source B state different values at same/overlapping time
            sample_vals = random.sample(v_pool, 2)
            val_a, val_b = sample_vals[0], sample_vals[1]
            src_a, src_b = "Primary_Sensor_Net", "Secondary_Sensor_Net"

            assertions = [
                {
                    "entity": entity,
                    "attribute": attr,
                    "value": val_a,
                    "timestamp": "2024-03-01T10:00:00Z",
                    "source": src_a,
                    "confidence": 0.85,
                    "is_deletion": False
                },
                {
                    "entity": entity,
                    "attribute": attr,
                    "value": val_b,
                    "timestamp": "2024-03-01T10:05:00Z",
                    "source": src_b,
                    "confidence": 0.85,
                    "is_deletion": False
                }
            ]

            return {
                "id": case_id,
                "split": split_name,
                "category": "CA",
                "assertions": assertions,
                "query": {
                    "entity": entity,
                    "attribute": attr,
                    "query_text": f"What is the verified {attr.replace('_', ' ')} of {entity}?",
                    "query_time": "2024-06-01T00:00:00Z"
                },
                "ground_truth": {
                    "expected_value": "CONFLICTED",
                    "expected_status": "CONFLICTED",
                    "conflicting_values": [val_a, val_b]
                }
            }

        elif category == "AU":
            # Abstention on Unknown: entity or attribute never asserted
            unasserted_attr = "emergency_contact_frequency"
            val = random.choice(v_pool)
            assertions = [
                {
                    "entity": entity,
                    "attribute": attr,
                    "value": val,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "source": source,
                    "confidence": 0.90,
                    "is_deletion": False
                }
            ]

            return {
                "id": case_id,
                "split": split_name,
                "category": "AU",
                "assertions": assertions,
                "query": {
                    "entity": entity,
                    "attribute": unasserted_attr,
                    "query_text": f"What is the {unasserted_attr.replace('_', ' ')} of {entity}?",
                    "query_time": "2024-06-01T00:00:00Z"
                },
                "ground_truth": {
                    "expected_value": "UNKNOWN",
                    "expected_status": "UNKNOWN"
                }
            }

        elif category == "TD":
            # Tombstone & Deletion: asserted at t1, explicitly deleted at t2
            val = random.choice(v_pool)
            assertions = [
                {
                    "entity": entity,
                    "attribute": attr,
                    "value": val,
                    "timestamp": "2024-01-10T08:00:00Z",
                    "source": source,
                    "confidence": 0.95,
                    "is_deletion": False
                },
                {
                    "entity": entity,
                    "attribute": attr,
                    "value": None,
                    "timestamp": "2024-04-12T16:00:00Z",
                    "source": "GDPR_User_Purge_Request",
                    "confidence": 1.0,
                    "is_deletion": True
                }
            ]

            return {
                "id": case_id,
                "split": split_name,
                "category": "TD",
                "assertions": assertions,
                "query": {
                    "entity": entity,
                    "attribute": attr,
                    "query_text": f"What is the stored {attr.replace('_', ' ')} of {entity}?",
                    "query_time": "2024-06-01T00:00:00Z"
                },
                "ground_truth": {
                    "expected_value": "DELETED",
                    "expected_status": "DELETED"
                }
            }

    categories = ["DR", "TR", "CA", "AU", "TD"]

    # Generate Pilot Split (30 cases: 6 per category)
    pilot_data = []
    for cat in categories:
        for i in range(6):
            cid = f"pilot_{cat}_{i+1:02d}"
            pilot_data.append(create_case(cid, cat, "pilot"))

    # Generate Held-out Split (60 cases: 12 per category)
    heldout_data = []
    for cat in categories:
        for i in range(12):
            cid = f"heldout_{cat}_{i+1:02d}"
            heldout_data.append(create_case(cid, cat, "heldout"))

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    with open(out_dir / "pilot_dataset.json", "w", encoding="utf-8") as f:
        json.dump(pilot_data, f, indent=2)

    with open(out_dir / "heldout_dataset.json", "w", encoding="utf-8") as f:
        json.dump(heldout_data, f, indent=2)

    print(f"Generated {len(pilot_data)} pilot cases -> data/pilot_dataset.json")
    print(f"Generated {len(heldout_data)} held-out cases -> data/heldout_dataset.json")


if __name__ == "__main__":
    generate_benchmark_splits()
