# src/domains/media/ — Media & Content domain
#
# Migrated (canonical location here, shim at original path):
#   src/domains/media/pipeline_graph.py  ✅ 2026-03-20
#     ← src/workflows/pipeline_graph.py (shim)
#   src/domains/media/content/           ✅ 2026-03-20
#     ← re-exports src/content/* (format_selector, topic_fit,
#       similarity_guard, engagement_plan, orio_scorer)
#   src/domains/media/writer.py          ✅ 2026-03-20
#     ← src/ai/claude_writer.py (shim)
#   src/domains/media/strategist.py      ✅ 2026-03-20
#     ← src/ai/gpt_strategist.py (shim)
#   src/domains/media/scorer.py          ✅ 2026-03-20
#     ← src/ai/claude_scorer.py (shim)
#
# Still to migrate (do NOT move until full test coverage confirmed):
#   (none remaining for media domain)
