"""Client tests."""
import pytest
from unittest.mock import Mock, patch
from propellerads import PropellerAdsClient

def test_client_init():
    client = PropellerAdsClient(api_key="test-key")
    assert client.config.api_key == "test-key"

@patch('propellerads.client.requests.Session')
def test_get_balance(mock_session):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '"1234.56"'
    mock_response.headers = {'content-type': 'text/plain'}
    mock_session.return_value.request.return_value = mock_response
    
    client = PropellerAdsClient(api_key="test-key")
    balance = client.get_balance()
    
    assert balance.amount == 1234.56
    assert balance.currency == "USD"

def test_health_check():
    with patch('propellerads.client.PropellerAdsClient.get_balance') as mock_balance:
        mock_balance.return_value = Mock(formatted="$1,234.56")
        
        client = PropellerAdsClient(api_key="test-key")
        health = client.health_check()
        
        assert health['overall_status'] in ['healthy', 'unhealthy']
