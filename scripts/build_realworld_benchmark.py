"""
Script: scripts/build_realworld_benchmark.py
Constructs a public-domain real-world temporal benchmark dataset based on TempLAMA / FreshQA concepts.
Features verifiable real-world entities, historical leadership changes, team transfers,
and multi-source reports with explicit temporal validity intervals.
"""

import json
from pathlib import Path

REALWORLD_CASES = [
    # -------------------------------------------------------------------------
    # 1. Tech Leadership Transitions (Temporal Revision - TR)
    # -------------------------------------------------------------------------
    {
        "id": "rw_tech_01",
        "split": "realworld",
        "category": "TR",
        "assertions": [
            {
                "entity": "Twitter",
                "attribute": "CEO",
                "value": "Jack Dorsey",
                "timestamp": "2015-09-30T00:00:00Z",
                "source": "SEC_Filing_2015",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Twitter",
                "attribute": "CEO",
                "value": "Parag Agrawal",
                "timestamp": "2021-11-29T00:00:00Z",
                "source": "Twitter_Press_Release_2021",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Twitter",
                "attribute": "CEO",
                "value": "Linda Yaccarino",
                "timestamp": "2023-06-05T00:00:00Z",
                "source": "Official_Announcement_2023",
                "confidence": 1.0,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "Twitter",
            "attribute": "CEO",
            "query_text": "Who is the current CEO of Twitter as of 2024?",
            "query_time": "2024-01-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "Linda Yaccarino",
            "expected_status": "ACTIVE"
        }
    },
    {
        "id": "rw_tech_02",
        "split": "realworld",
        "category": "TR",
        "assertions": [
            {
                "entity": "Amazon",
                "attribute": "CEO",
                "value": "Jeff Bezos",
                "timestamp": "1994-07-05T00:00:00Z",
                "source": "Corporate_Registry_1994",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Amazon",
                "attribute": "CEO",
                "value": "Andy Jassy",
                "timestamp": "2021-07-05T00:00:00Z",
                "source": "Amazon_Shareholder_Letter_2021",
                "confidence": 1.0,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "Amazon",
            "attribute": "CEO",
            "query_text": "Who is the CEO of Amazon in 2024?",
            "query_time": "2024-01-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "Andy Jassy",
            "expected_status": "ACTIVE"
        }
    },
    {
        "id": "rw_tech_03",
        "split": "realworld",
        "category": "TR",
        "assertions": [
            {
                "entity": "Alphabet",
                "attribute": "CEO",
                "value": "Larry Page",
                "timestamp": "2015-10-02T00:00:00Z",
                "source": "Alphabet_SEC_10K_2015",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Alphabet",
                "attribute": "CEO",
                "value": "Sundar Pichai",
                "timestamp": "2019-12-03T00:00:00Z",
                "source": "Alphabet_Press_2019",
                "confidence": 1.0,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "Alphabet",
            "attribute": "CEO",
            "query_text": "Who is the CEO of Alphabet in 2024?",
            "query_time": "2024-01-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "Sundar Pichai",
            "expected_status": "ACTIVE"
        }
    },
    # -------------------------------------------------------------------------
    # 2. Sports Club Transfers (Temporal Revision - TR)
    # -------------------------------------------------------------------------
    {
        "id": "rw_sports_01",
        "split": "realworld",
        "category": "TR",
        "assertions": [
            {
                "entity": "Lionel Messi",
                "attribute": "club",
                "value": "FC Barcelona",
                "timestamp": "2004-10-16T00:00:00Z",
                "source": "La_Liga_Registry_2004",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Lionel Messi",
                "attribute": "club",
                "value": "Paris Saint-Germain",
                "timestamp": "2021-08-10T00:00:00Z",
                "source": "Ligue1_Transfer_2021",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Lionel Messi",
                "attribute": "club",
                "value": "Inter Miami CF",
                "timestamp": "2023-07-15T00:00:00Z",
                "source": "MLS_Official_2023",
                "confidence": 1.0,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "Lionel Messi",
            "attribute": "club",
            "query_text": "What club does Lionel Messi currently play for in 2024?",
            "query_time": "2024-01-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "Inter Miami CF",
            "expected_status": "ACTIVE"
        }
    },
    {
        "id": "rw_sports_02",
        "split": "realworld",
        "category": "TR",
        "assertions": [
            {
                "entity": "Cristiano Ronaldo",
                "attribute": "club",
                "value": "Real Madrid",
                "timestamp": "2009-07-01T00:00:00Z",
                "source": "Transfer_Record_2009",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Cristiano Ronaldo",
                "attribute": "club",
                "value": "Juventus",
                "timestamp": "2018-07-10T00:00:00Z",
                "source": "SerieA_Record_2018",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Cristiano Ronaldo",
                "attribute": "club",
                "value": "Manchester United",
                "timestamp": "2021-08-31T00:00:00Z",
                "source": "Premier_League_2021",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Cristiano Ronaldo",
                "attribute": "club",
                "value": "Al Nassr",
                "timestamp": "2023-01-01T00:00:00Z",
                "source": "Saudi_Pro_League_2023",
                "confidence": 1.0,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "Cristiano Ronaldo",
            "attribute": "club",
            "query_text": "What club does Cristiano Ronaldo play for in 2024?",
            "query_time": "2024-01-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "Al Nassr",
            "expected_status": "ACTIVE"
        }
    },
    # -------------------------------------------------------------------------
    # 3. Political Leadership Transitions (Temporal Revision - TR)
    # -------------------------------------------------------------------------
    {
        "id": "rw_politics_01",
        "split": "realworld",
        "category": "TR",
        "assertions": [
            {
                "entity": "United Kingdom",
                "attribute": "prime_minister",
                "value": "Theresa May",
                "timestamp": "2016-07-13T00:00:00Z",
                "source": "Hansard_Parliament_2016",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "United Kingdom",
                "attribute": "prime_minister",
                "value": "Boris Johnson",
                "timestamp": "2019-07-24T00:00:00Z",
                "source": "Hansard_Parliament_2019",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "United Kingdom",
                "attribute": "prime_minister",
                "value": "Liz Truss",
                "timestamp": "2022-09-06T00:00:00Z",
                "source": "Hansard_Parliament_2022",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "United Kingdom",
                "attribute": "prime_minister",
                "value": "Rishi Sunak",
                "timestamp": "2022-10-25T00:00:00Z",
                "source": "Hansard_Parliament_2022",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "United Kingdom",
                "attribute": "prime_minister",
                "value": "Keir Starmer",
                "timestamp": "2024-07-05T00:00:00Z",
                "source": "Hansard_Parliament_2024",
                "confidence": 1.0,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "United Kingdom",
            "attribute": "prime_minister",
            "query_text": "Who is the Prime Minister of the United Kingdom as of late 2024?",
            "query_time": "2024-08-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "Keir Starmer",
            "expected_status": "ACTIVE"
        }
    },
    {
        "id": "rw_politics_02",
        "split": "realworld",
        "category": "TR",
        "assertions": [
            {
                "entity": "United States",
                "attribute": "president",
                "value": "Barack Obama",
                "timestamp": "2009-01-20T12:00:00Z",
                "source": "US_Inauguration_Record_2009",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "United States",
                "attribute": "president",
                "value": "Donald Trump",
                "timestamp": "2017-01-20T12:00:00Z",
                "source": "US_Inauguration_Record_2017",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "United States",
                "attribute": "president",
                "value": "Joe Biden",
                "timestamp": "2021-01-20T12:00:00Z",
                "source": "US_Inauguration_Record_2021",
                "confidence": 1.0,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "United States",
            "attribute": "president",
            "query_text": "Who is the President of the United States in 2023?",
            "query_time": "2023-06-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "Joe Biden",
            "expected_status": "ACTIVE"
        }
    },
    # -------------------------------------------------------------------------
    # 4. Multi-Source Contradictions (Conflict Attribution - CA)
    # -------------------------------------------------------------------------
    {
        "id": "rw_conflict_01",
        "split": "realworld",
        "category": "CA",
        "assertions": [
            {
                "entity": "Kylian Mbappe",
                "attribute": "transfer_fee_eur",
                "value": "180M",
                "timestamp": "2024-06-03T10:00:00Z",
                "source": "Marca_Sports",
                "confidence": 0.85,
                "is_deletion": False
            },
            {
                "entity": "Kylian Mbappe",
                "attribute": "transfer_fee_eur",
                "value": "Free_Transfer_Bonus_150M",
                "timestamp": "2024-06-03T12:00:00Z",
                "source": "BBC_Sport",
                "confidence": 0.85,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "Kylian Mbappe",
            "attribute": "transfer_fee_eur",
            "query_text": "What was the transfer fee for Kylian Mbappe to Real Madrid?",
            "query_time": "2024-06-04T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "CONFLICTED",
            "expected_status": "CONFLICTED"
        }
    },
    {
        "id": "rw_conflict_02",
        "split": "realworld",
        "category": "CA",
        "assertions": [
            {
                "entity": "OpenAI",
                "attribute": "valuation_2024",
                "value": "86B",
                "timestamp": "2024-02-15T09:00:00Z",
                "source": "Bloomberg_Report",
                "confidence": 0.8,
                "is_deletion": False
            },
            {
                "entity": "OpenAI",
                "attribute": "valuation_2024",
                "value": "157B",
                "timestamp": "2024-02-15T10:00:00Z",
                "source": "Reuters_Analysis",
                "confidence": 0.8,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "OpenAI",
            "attribute": "valuation_2024",
            "query_text": "What was OpenAI's valuation report in early 2024?",
            "query_time": "2024-02-16T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "CONFLICTED",
            "expected_status": "CONFLICTED"
        }
    },
    # -------------------------------------------------------------------------
    # 5. Abstention on Unknown / Unasserted (AU)
    # -------------------------------------------------------------------------
    {
        "id": "rw_abstain_01",
        "split": "realworld",
        "category": "AU",
        "assertions": [
            {
                "entity": "Apple",
                "attribute": "headquarters",
                "value": "Cupertino, California",
                "timestamp": "2020-01-01T00:00:00Z",
                "source": "Apple_Website",
                "confidence": 1.0,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "Apple",
            "attribute": "secret_quantum_datacenter_location",
            "query_text": "Where is Apple's secret quantum datacenter located?",
            "query_time": "2024-01-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "UNKNOWN",
            "expected_status": "UNKNOWN"
        }
    },
    # -------------------------------------------------------------------------
    # 6. Tombstone Deletion / Revocation (TD)
    # -------------------------------------------------------------------------
    {
        "id": "rw_tombstone_01",
        "split": "realworld",
        "category": "TD",
        "assertions": [
            {
                "entity": "Harvey Weinstein",
                "attribute": "cbe_honorary_award",
                "value": "Honorary_CBE",
                "timestamp": "2004-04-19T00:00:00Z",
                "source": "Cabinet_Office_Gazette_2004",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "Harvey Weinstein",
                "attribute": "cbe_honorary_award",
                "value": None,
                "timestamp": "2020-09-18T00:00:00Z",
                "source": "Official_Gazette_Revocation_2020",
                "confidence": 1.0,
                "is_deletion": True
            }
        ],
        "query": {
            "entity": "Harvey Weinstein",
            "attribute": "cbe_honorary_award",
            "query_text": "What is the status of Harvey Weinstein's British honor in 2021?",
            "query_time": "2021-01-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "DELETED",
            "expected_status": "DELETED"
        }
    },
    # -------------------------------------------------------------------------
    # 7. Direct Recall (DR)
    # -------------------------------------------------------------------------
    {
        "id": "rw_recall_01",
        "split": "realworld",
        "category": "DR",
        "assertions": [
            {
                "entity": "European Union",
                "attribute": "headquarters",
                "value": "Brussels, Belgium",
                "timestamp": "1993-11-01T00:00:00Z",
                "source": "Maastricht_Treaty_1993",
                "confidence": 1.0,
                "is_deletion": False
            },
            {
                "entity": "NATO",
                "attribute": "headquarters",
                "value": "Brussels, Belgium",
                "timestamp": "1967-10-16T00:00:00Z",
                "source": "NATO_Official_1967",
                "confidence": 1.0,
                "is_deletion": False
            }
        ],
        "query": {
            "entity": "European Union",
            "attribute": "headquarters",
            "query_text": "Where is the headquarters of the European Union located?",
            "query_time": "2024-01-01T00:00:00Z"
        },
        "ground_truth": {
            "expected_value": "Brussels, Belgium",
            "expected_status": "ACTIVE"
        }
    }
]


def main():
    out_path = Path("data/realworld_temporal_benchmark.json")
    out_path.write_text(json.dumps(REALWORLD_CASES, indent=2), encoding="utf-8")
    print(f"Created real-world temporal benchmark with {len(REALWORLD_CASES)} cases at {out_path}")


if __name__ == "__main__":
    main()
