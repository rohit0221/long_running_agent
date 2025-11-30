from target_repo.src.utils.analytics import AnalyticsEngine

def test_track_event():
    engine = AnalyticsEngine()
    engine.track_event("login")
    assert len(engine.data) == 1