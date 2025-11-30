import pytest
from target_repo.src.utils.analytics import AnalyticsEngine


def test_track_event_basic_and_get_events():
    eng = AnalyticsEngine()
    eng.track_event("login")
    eng.track_event("login", {"user": "alice"})
    eng.track_event("purchase", {"item": "book"})

    assert len(eng.data) == 3

    login_events = eng.get_events("login")
    assert len(login_events) == 2
    assert login_events[0]["name"] == "login"
    assert login_events[0]["properties"] == {}
    assert login_events[1]["properties"] == {"user": "alice"}

    purchase_events = eng.get_events("purchase")
    assert len(purchase_events) == 1
    assert purchase_events[0]["properties"] == {"item": "book"}


def test_track_event_empty_name_raises():
    eng = AnalyticsEngine()
    with pytest.raises(ValueError):
        eng.track_event("", {"anything": "value"})


def test_clear_resets():
    eng = AnalyticsEngine()
    eng.track_event("event1")
    eng.track_event("event2", {"a": 1})

    assert len(eng.data) == 2
    eng.clear()
    assert eng.data == []
    assert eng.get_events("event1") == []


def test_get_events_filters_by_name():
    eng = AnalyticsEngine()
    eng.track_event("A", {"k": 1})
    eng.track_event("B", {"k": 2})
    eng.track_event("A", {"k": 3})

    events_A = eng.get_events("A")
    assert len(events_A) == 2
    assert all(e["name"] == "A" for e in events_A)

    events_B = eng.get_events("B")
    assert len(events_B) == 1


def test_mutation_of_event_in_get_events_reflects_in_data():
    eng = AnalyticsEngine()
    eng.track_event("mutable", {"count": 0})
    events = eng.get_events("mutable")
    assert len(events) == 1

    event = events[0]
    event["properties"]["count"] = 42
    assert eng.data[0]["properties"]["count"] == 42