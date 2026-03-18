"""Tests for Plottwist."""
from src.core import Plottwist
def test_init(): assert Plottwist().get_stats()["ops"] == 0
def test_op(): c = Plottwist(); c.generate(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Plottwist(); [c.generate() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Plottwist(); c.generate(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Plottwist(); r = c.generate(); assert r["service"] == "plottwist"
