# src/domains/trading/ — Trading domain (CoinCat, future isolated context)
# Status: DEFERRED — do not implement until approval enforcement is stronger
#         and this domain can run in full isolation from media/flow_lab.
# Planned modules (spec only):
#   trading/data_ingest.py      — price/volume feed ingestion
#   trading/market_structure.py — trend/range classification
#   trading/setup_detector.py   — pattern recognition
#   trading/journal.py          — trade log
#   trading/playbook.py         — rule-based playbook runner
