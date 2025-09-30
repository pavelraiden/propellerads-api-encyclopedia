"""Client tests."""
import pytest
from unittest.mock import Mock, patch
from propellerads import LegacyPropellerAdsClient as PropellerAdsClient

def test_client_init():
    """Test client initialization."""
    client = PropellerAdsClient(api_key="test-key")
    assert hasattr(client.config, 'api_key')
    assert client.config.api_key == "test-key"

@patch('requests.Session.request')
def test_get_balance(mock_request):
    """Test balance retrieval."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '1234.56'
    mock_response.headers = {'content-type': 'text/plain'}
    mock_request.return_value = mock_response
    
    client = PropellerAdsClient(api_key="test-key")
    balance = client.get_balance()
    
    assert float(balance.amount) == 1234.56
    assert balance.currency == "USD"

def test_health_check():
    """Test health check."""
    with patch('propellerads.client.PropellerAdsClient.get_balance') as mock_balance:
        mock_balance.return_value = Mock(formatted="$1,234.56")
        
        client = PropellerAdsClient(api_key="test-key")
        health = client.health_check()
        
        assert health['overall_status'] in ['healthy', 'unhealthy']
