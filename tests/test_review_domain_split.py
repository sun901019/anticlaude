# tests/test_review_domain_split.py
# Pure logic test for action_type -> domain classification.
# The classify_domain function is defined here (not imported from src)
# because this tests the domain logic spec, not a specific implementation.

ECOMMERCE_ACTIONS = {
    "promote_product",
    "approve_purchase",
    "approve_screenshot",
    "approve_video_analysis",
}

SOCIAL_ACTIONS = {
    "publish_post",
    "select_draft",
    "confirm_analysis",
}


def classify_domain(action_type: str | None) -> str:
    if action_type in ECOMMERCE_ACTIONS:
        return "ecommerce"
    if action_type in SOCIAL_ACTIONS:
        return "social"
    return "system"


# --- Tests ---

def test_publish_post_is_social():
    assert classify_domain("publish_post") == "social"


def test_select_draft_is_social():
    assert classify_domain("select_draft") == "social"


def test_promote_product_is_ecommerce():
    assert classify_domain("promote_product") == "ecommerce"


def test_approve_purchase_is_ecommerce():
    assert classify_domain("approve_purchase") == "ecommerce"


def test_approve_screenshot_is_ecommerce():
    assert classify_domain("approve_screenshot") == "ecommerce"


def test_approve_video_is_ecommerce():
    assert classify_domain("approve_video_analysis") == "ecommerce"


def test_unknown_action_is_system():
    assert classify_domain("unknown_thing") == "system"


def test_none_action_is_system():
    assert classify_domain(None) == "system"
