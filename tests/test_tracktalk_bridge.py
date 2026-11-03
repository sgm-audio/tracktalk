"""TrackTalk parser tests — regression coverage for TRA-01..TRA-04."""

from tracktalk_bridge import TrackTalk


def test_pan_bass_left_parses():
    """TRA-02: 'Pan bass left' must parse (non-contiguous 'pan left')."""
    tt = TrackTalk()
    c = tt.parse("Pan bass left")
    assert c is not None
    assert c["action"] == "pan_left"
    assert c["target"] == "bass"


def test_reverb_rhythm_target():
    """TRA-03: 'Add reverb to rhythm' targets rhythm, not track 1 fallback."""
    tt = TrackTalk()
    c = tt.parse("Add reverb to rhythm")
    assert c is not None
    assert c["action"] == "fx_reverb"
    assert c["target"] == "rhythm"


def test_plus_db_is_relative_gain_up():
    """TRA-04: '+2dB vocals' is gain_up (relative increase), not None."""
    tt = TrackTalk()
    c = tt.parse("+2dB vocals")
    assert c is not None
    assert c["action"] == "gain_up"
    assert c["target"] == "vocals"
    assert c["param"] == 2.0


def test_minus_db_is_relative_gain_down():
    """TRA-04: '-3dB drums' is gain_down (relative decrease), not None."""
    tt = TrackTalk()
    c = tt.parse("-3dB drums")
    assert c is not None
    assert c["action"] == "gain_down"
    assert c["target"] == "drums"
    assert c["param"] == 3.0


def test_louder_still_works():
    tt = TrackTalk()
    c = tt.parse("louder vocals")
    assert c is not None
    assert c["action"] == "gain_up"
    assert c["target"] == "vocals"


def test_pan_left_still_works():
    tt = TrackTalk()
    c = tt.parse("pan left bass")
    assert c is not None
    assert c["action"] == "pan_left"
    assert c["target"] == "bass"


def test_mute_still_works():
    tt = TrackTalk()
    c = tt.parse("mute drums")
    assert c is not None
    assert c["action"] == "mute"
    assert c["target"] == "drums"


def test_unknown_command_returns_none():
    tt = TrackTalk()
    assert tt.parse("frobnicate the widget") is None
