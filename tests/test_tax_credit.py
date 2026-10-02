"""Tests for Tax Credit Engine."""

from tax_credit_advisor import agents, engine
from tax_credit_advisor.data import SITES
from tax_credit_advisor.trail import TrailRecorder


def test_ga_qualifies_anchor():
    r = engine.compute_credit(SITES["GA"], engine.load_pack("GA"))
    assert r.net_new == 20.0
    assert r.qualifying_jobs == 20.0
    assert r.annual_credit == 60000.0
    assert r.lifetime_credit == 300000.0


def test_nc_is_the_discovery():
    r = engine.compute_credit(SITES["NC"], engine.load_pack("NC"))
    assert r.qualifying_jobs == 15.0
    assert r.lifetime_credit == 150000.0


def test_sc_below_threshold_is_zero():
    r = engine.compute_credit(SITES["SC"], engine.load_pack("SC"))
    assert r.qualifying_jobs == 0.0
    assert r.lifetime_credit == 0.0


def test_ny_contracting_is_zero():
    r = engine.compute_credit(SITES["NY"], engine.load_pack("NY"))
    assert r.net_new == -5.0
    assert r.qualifying_jobs == 0.0


def test_tx_has_no_pack():
    r = engine.compute_credit(SITES["TX"], engine.load_pack("TX"))
    assert r.has_pack is False
    assert r.lifetime_credit == 0.0


def test_simulate_positive_delta():
    r = engine.simulate("GA", 10.0)
    assert r.net_new == 30.0
    assert r.lifetime_credit == 450000.0


def test_trail_fingerprint_is_deterministic():
    t1 = TrailRecorder()
    engine.compute_credit(SITES["GA"], engine.load_pack("GA"), t1)
    t2 = TrailRecorder()
    engine.compute_credit(SITES["GA"], engine.load_pack("GA"), t2)
    assert t1.fingerprint() == t2.fingerprint()


def test_narration_restates_engine_numbers():
    r = engine.compute_credit(SITES["GA"], engine.load_pack("GA"))
    text = agents.credit_narration(r)
    assert "$60,000" in text and "$300,000" in text
