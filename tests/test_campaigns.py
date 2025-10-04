import pytest
import vcr
from propellerads.client import PropellerAdsClient

@pytest.fixture
def client():
    return PropellerAdsClient(api_key="test_api_key")

@vcr.use_cassette("tests/cassettes/get_campaign_by_id.yml")
def test_get_campaign_by_id(client):
    """Test getting campaign by ID"""
    campaign = client.get_campaign_by_id(campaign_id=9446595)
    assert isinstance(campaign, dict)
    assert campaign["id"] == 9446595
    assert "name" in campaign
    assert "status" in campaign
