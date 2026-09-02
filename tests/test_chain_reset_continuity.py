from pathlib import Path
from unittest import mock

from series import critic
from series.bible import Bible


def _bible() -> Bible:
    return Bible({
        "series": {"slug": "chain-proof", "title": "Chain Proof", "engine": "omni"},
        "characters": [],
        "environments": [],
        "props": [],
    })


def _chain_review(**changes) -> dict:
    review = {
        "anatomy_ok": True,
        "unwanted_text": False,
        "forbidden_elements": False,
        "artifact_score": 1,
        "object_match": False,
        "state_carry_ok": {"value": True, "visible": True, "confidence": 0.95},
        "chain_frame_suitable": True,
        "chain_frame_notes": "stable terminal state",
    }
    review.update(changes)
    return review


def _review_terminal(review: dict):
    shot = {"n": 3, "state_carry": "the tines stretched long and empty"}
    qc = {"require_object_match": True, "artifact_threshold": 7}
    with mock.patch.object(critic, "_review_frames", return_value=review):
        return critic.review_chain_frame(
            _bible(), shot, Path("last.jpg"), "fork prompt", qc,
            object_ref=b"reference", episode=26,
        )


def test_intended_terminal_deformation_preserves_chain_identity():
    suitable, reasons = _review_terminal(_chain_review())
    assert suitable is True
    assert reasons == []


def test_real_chain_frame_artifact_is_still_rejected():
    suitable, reasons = _review_terminal(_chain_review(
        artifact_score=9,
        issues=["blurred, cropped fork and dissolved counter edge"],
    ))
    assert suitable is False
    assert any("artifact" in reason for reason in reasons)


def test_real_object_identity_shift_is_still_rejected():
    suitable, reasons = _review_terminal(_chain_review(
        state_carry_ok={"value": False, "visible": True, "confidence": 0.99},
    ))
    assert suitable is False
    assert any("aynı fiziksel obje" in reason for reason in reasons)


def test_reset_exempts_false_continuity_for_next_shot():
    verdict, reasons = critic._decide(
        {"continuity_ok": False, "artifact_score": 0},
        {"artifact_threshold": 7, "require_continuity": True,
         "_continuity_exempt": True},
        False, 4,
    )
    assert verdict == "pass"
    assert reasons == []


def test_reset_exempts_unevaluated_continuity_for_next_shot():
    verdict, reasons = critic._decide(
        {"artifact_score": 0},
        {"artifact_threshold": 7, "require_continuity": True,
         "_continuity_exempt": True},
        False, 4,
    )
    assert verdict == "pass"
    assert reasons == []


def test_false_continuity_without_reset_is_still_rejected():
    verdict, reasons = critic._decide(
        {"continuity_ok": False, "artifact_score": 0},
        {"artifact_threshold": 7, "require_continuity": True},
        False, 4,
    )
    assert verdict == "fail"
    assert any("sürekliliği bozuk" in reason for reason in reasons)


def test_reset_exemption_does_not_leak_to_following_shot():
    first, _ = critic._decide(
        {"continuity_ok": False, "artifact_score": 0},
        {"artifact_threshold": 7, "require_continuity": True,
         "_continuity_exempt": True},
        False, 4,
    )
    following, reasons = critic._decide(
        {"continuity_ok": False, "artifact_score": 0},
        {"artifact_threshold": 7, "require_continuity": True,
         "_continuity_exempt": False},
        False, 4,
    )
    assert first == "pass"
    assert following == "fail"
    assert any("sürekliliği bozuk" in reason for reason in reasons)


def test_series_exemption_notes_still_reach_chain_reviewer():
    notes = "SERIES EXEMPTION: intended shape change"
    shot = {"n": 3, "state_carry": "the tines stretched long and empty"}
    qc = {"require_object_match": True, "artifact_threshold": 7, "notes": notes}
    with mock.patch.object(critic, "_review_frames", return_value=_chain_review()) as review:
        critic.review_chain_frame(
            _bible(), shot, Path("last.jpg"), "fork prompt", qc,
            object_ref=b"reference", episode=26,
        )
    assert review.call_args.args[3] == notes
    assert review.call_args.kwargs["state_carry_expected"] == shot["state_carry"]
    assert review.call_args.kwargs["chain_frame_identity"] is True
