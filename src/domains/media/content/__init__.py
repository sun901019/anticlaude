"""
src/domains/media/content/ — Media content intelligence shim package.

Re-exports all content intelligence modules from the legacy src/content/ location.
Canonical migration target: move each module here when ready.

Current modules (still at src/content/):
  - format_selector   → FormatSelector, select_format
  - topic_fit         → TopicFitResult, check_topic_fit
  - similarity_guard  → SimilarityGuard
  - engagement_plan   → EngagementPlan
  - orio_scorer       → OrioScore, score_topic, rank_topics
"""
from src.content.format_selector import FormatRecommendation, select_format  # noqa: F401
from src.content.topic_fit import TopicFitResult, check_topic_fit  # noqa: F401
from src.content.similarity_guard import SimilarityResult, check_similarity  # noqa: F401
from src.content.engagement_plan import EngagementPlan, build_engagement_plan  # noqa: F401
from src.content.orio_scorer import OrioScore, score_topic, rank_topics  # noqa: F401
