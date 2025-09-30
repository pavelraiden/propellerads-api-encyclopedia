#!/usr/bin/env python3
"""
Comprehensive tests for the PropellerAds Python SDK.
"""

import pytest
import os
import time
import requests
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock

from propellerads.client import PropellerAdsClient, BalanceResponse
from propellerads.async_client import AsyncPropellerAdsClient
from propellerads.exceptions import PropellerAdsError, AuthenticationError, RateLimitError


class TestPropellerAdsClient:
    """Tests for the synchronous client."""

    def setup_method(self):
        """Set up test client."""
        self.client = PropellerAdsClient(api_key="test_api_key")

    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.config.api_key == "test_api_key"
        assert self.client.config.base_url == "https://ssp-api.propellerads.com/v5"
        assert hasattr(self.client, 'session')

    @patch('requests.Session.request')
    def test_get_balance_success(self, mock_request):
        """Test successful balance retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '1686.48'
        mock_request.return_value = mock_response

        result = self.client.get_balance()

        assert isinstance(result, BalanceResponse)
        assert result.amount == Decimal("1686.48")
        assert result.currency == "USD"

    @patch('requests.Session.request')
    def test_get_campaigns_success(self, mock_request):
        """Test successful campaign retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': [{'id': 1, 'name': 'Test Campaign'}],
            'total': 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_campaigns()

        assert isinstance(result, dict)
        assert 'result' in result
        assert len(result['result']) == 1
        assert result['result'][0]['id'] == 1

    @patch('requests.Session.request')
    def test_health_check_success(self, mock_request):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '1000.00'
        mock_request.return_value = mock_response

        result = self.client.health_check()

        assert result['overall_status'] == 'healthy'
        assert 'balance' in result
        assert 'rate_limiter' in result

    @patch('requests.Session.request')
    def test_make_request_error_handling(self, mock_request):
        """Test error handling in _make_request."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'error': 'Not found'}
        mock_request.return_value = mock_response

        with pytest.raises(PropellerAdsError):
            self.client._make_request('GET', '/nonexistent')

    @patch('requests.Session.request')
    def test_get_statistics_success(self, mock_request):
        """Test successful statistics retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': [{'date': '2025-09-30', 'impressions': 1000, 'clicks': 100}],
            'total': 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_statistics(date_from="2025-09-30 00:00:00", date_to="2025-09-30 23:59:59")

        assert isinstance(result, dict)
        assert 'result' in result
        assert len(result['result']) == 1
        assert result['result'][0]['impressions'] == 1000

    @patch('requests.Session.request')
    def test_get_statistics_invalid_date_format(self, mock_request):
        """Test get_statistics with an invalid date format."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Invalid date format'}
        mock_request.return_value = mock_response

        with pytest.raises(PropellerAdsError):
            self.client.get_statistics(date_from="2025-30-09", date_to="2025-30-09")

    @patch('requests.Session.request')
    def test_circuit_breaker_opens(self, mock_request):
        """Test that the circuit breaker opens after multiple failures."""
        # Mock consecutive failures
        mock_request.side_effect = requests.exceptions.RequestException('Connection error')
        
        # Set a low failure threshold for testing
        self.client.circuit_breaker['failure_threshold'] = 3

        # Trigger failures to open the circuit breaker
        for _ in range(4):  # One more than threshold
            with pytest.raises(PropellerAdsError):
                self.client.get_balance()

        # Verify circuit breaker is open
        assert self.client.circuit_breaker['state'] == 'open'
        assert self.client.circuit_breaker['failures'] >= 3

        # Check that subsequent calls fail immediately because the circuit is open
        with pytest.raises(PropellerAdsError, match='Circuit breaker is open'):
            self.client.get_balance()

    def test_rate_limiter(self):
        """Test that the rate limiter works correctly."""
        # Test rate limiter status and functionality
        client = PropellerAdsClient(api_key="test_api_key", rate_limit=60)
        
        # Check rate limiter is initialized
        assert hasattr(client, 'rate_limiter')
        assert client.rate_limiter is not None
        
        # Test rate limiter status
        status = client.rate_limiter.get_status()
        assert 'tokens_available' in status
        assert 'bucket_size' in status
        assert 'refill_rate' in status
        
        # Test rate limiter acquire
        success = client.rate_limiter.try_acquire(1)
        assert success is True  # Should succeed with tokens available

    @patch('requests.Session.request')
    def test_create_campaign_success(self, mock_request):
        """Test successful campaign creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 123,
            'name': 'New Campaign',
            'direction': 'popunder',
            'rate_model': 'cpm',
            'target_url': 'http://example.com',
            'status': 1,
        }
        mock_request.return_value = mock_response

        campaign_data = {
            'name': 'New Campaign',
            'direction': 'popunder',
            'rate_model': 'cpm',
            'target_url': 'http://example.com',
        }

        result = self.client.create_campaign(campaign_data)

        assert isinstance(result, dict)
        assert result['id'] == 123
        assert result['name'] == 'New Campaign'

    @patch('requests.Session.request')
    def test_update_campaign_success(self, mock_request):
        """Test successful campaign update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 123,
            'name': 'Updated Campaign',
            'status': 2,
        }
        mock_request.return_value = mock_response

        campaign_data = {
            'name': 'Updated Campaign',
            'status': 2,
        }

        result = self.client.update_campaign(123, campaign_data)

        assert isinstance(result, dict)
        assert result['id'] == 123
        assert result['name'] == 'Updated Campaign'
        assert result['status'] == 2

    @patch('requests.Session.request')
    def test_delete_campaign_success(self, mock_request):
        """Test successful campaign deletion."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        try:
            self.client.delete_campaign(123)
        except Exception as e:
            pytest.fail(f"Deleting a campaign should not raise an exception. Raised: {e}")

    @patch('requests.Session.request')
    def test_get_advertisers_success(self, mock_request):
        """Test successful advertisers retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': [{'id': 1, 'name': 'Advertiser 1'}],
            'total': 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_advertisers()

        assert isinstance(result, dict)
        assert 'result' in result
        assert len(result['result']) == 1
        assert result['result'][0]['id'] == 1

    @patch('requests.Session.request')
    def test_get_campaign_groups_success(self, mock_request):
        """Test successful campaign groups retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': [{'id': 1, 'name': 'Campaign Group 1'}],
            'total': 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_campaign_groups()

        assert isinstance(result, dict)
        assert 'result' in result
        assert len(result['result']) == 1
        assert result['result'][0]['id'] == 1

    @patch("requests.Session.request")
    def test_get_notifications_success(self, mock_request):
        """Test successful notifications retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "message": "Test Notification"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_notifications()

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == 1

    @patch("requests.Session.request")
    def test_get_user_profile_success(self, mock_request):
        """Test successful user profile retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 12345,
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_request.return_value = mock_response

        result = self.client.get_user_profile()

        assert isinstance(result, dict)
        assert result["id"] == 12345
        assert result["email"] == "test@example.com"

    @patch("requests.Session.request")
    def test_get_targeting_options_success(self, mock_request):
        """Test successful targeting options retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "countries": [{"id": "US", "name": "United States"}],
            "browsers": [{"id": "chrome", "name": "Chrome"}]
        }
        mock_request.return_value = mock_response

        result = self.client.get_targeting_options()

        assert isinstance(result, dict)
        assert "countries" in result
        assert len(result["countries"]) == 1

    @patch("requests.Session.request")
    def test_get_creatives_success(self, mock_request):
        """Test successful creatives retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "name": "Creative 1"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_creatives()

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == 1

    @patch("requests.Session.request")
    def test_get_user_settings_success(self, mock_request):
        """Test successful user settings retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "notifications": {
                "news": True,
                "webinars": False
            }
        }
        mock_request.return_value = mock_response

        result = self.client.get_user_settings()

        assert isinstance(result, dict)
        assert "notifications" in result
        assert result["notifications"]["news"] is True

    @patch("requests.Session.request")
    def test_get_user_activity_success(self, mock_request):
        """Test successful user activity retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"event": "login", "timestamp": "2025-09-30T12:00:00Z"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_user_activity()

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["event"] == "login"

    @patch("requests.Session.request")
    def test_get_user_invoices_success(self, mock_request):
        """Test successful user invoices retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": "inv_123", "amount": 100.00, "status": "paid"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_user_invoices()

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == "inv_123"

    @patch("requests.Session.request")
    def test_get_user_referral_success(self, mock_request):
        """Test successful user referral retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "referral_link": "https://propellerads.com/?ref_id=123",
            "earned_amount": 50.00
        }
        mock_request.return_value = mock_response

        result = self.client.get_user_referral()

        assert isinstance(result, dict)
        assert "referral_link" in result
        assert result["earned_amount"] == 50.00

    @patch("requests.Session.request")
    def test_get_user_payments_success(self, mock_request):
        """Test successful user payments retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": "pay_123", "amount": 100.00, "status": "completed"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_user_payments()

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == "pay_123"

    @patch("requests.Session.request")
    def test_get_promo_codes_success(self, mock_request):
        """Test successful promo codes retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"code": "PROMO10", "discount": "10%"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_promo_codes()

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["code"] == "PROMO10"

    @patch("requests.Session.request")
    def test_change_password_success(self, mock_request):
        """Test successful password change."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = self.client.change_password("old_password", "new_password")

        assert isinstance(result, dict)
        assert result["success"] is True

    @patch("requests.Session.request")
    def test_change_email_success(self, mock_request):
        """Test successful email change."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = self.client.change_email("new@example.com")

        assert isinstance(result, dict)
        assert result["success"] is True

    @patch("requests.Session.request")
    def test_update_notifications_success(self, mock_request):
        """Test successful notification settings update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        settings = {"news": False, "webinars": True}
        result = self.client.update_notifications(settings)

        assert isinstance(result, dict)
        assert result["success"] is True

    @patch("requests.Session.request")
    def test_get_token_success(self, mock_request):
        """Test successful token retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "new_token_123"}
        mock_request.return_value = mock_response

        result = self.client.get_token()

        assert isinstance(result, dict)
        assert result["token"] == "new_token_123"

    @patch("requests.Session.request")
    def test_get_managers_success(self, mock_request):
        """Test successful managers retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "name": "Manager 1"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_managers()

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == 1

    @patch("requests.Session.request")
    def test_get_collections_success(self, mock_request):
        """Test successful collections retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "name": "Collection 1"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_collections()

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == 1

    @patch("requests.Session.request")
    def test_create_creative_success(self, mock_request):
        """Test successful creative creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 123,
            "name": "New Creative",
            "url": "http://example.com/creative.jpg",
        }
        mock_request.return_value = mock_response

        creative_data = {
            "name": "New Creative",
            "url": "http://example.com/creative.jpg",
        }

        result = self.client.create_creative(creative_data)

        assert isinstance(result, dict)
        assert result["id"] == 123
        assert result["name"] == "New Creative"

    @patch("requests.Session.request")
    def test_update_creative_success(self, mock_request):
        """Test successful creative update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "name": "Updated Creative",
        }
        mock_request.return_value = mock_response

        creative_data = {
            "name": "Updated Creative",
        }

        result = self.client.update_creative(123, creative_data)

        assert isinstance(result, dict)
        assert result["id"] == 123
        assert result["name"] == "Updated Creative"

    @patch("requests.Session.request")
    def test_delete_creative_success(self, mock_request):
        """Test successful creative deletion."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        try:
            self.client.delete_creative(123)
        except Exception as e:
            pytest.fail(f"Deleting a creative should not raise an exception. Raised: {e}")

    @patch("requests.Session.request")
    def test_get_zones_success(self, mock_request):
        """Test successful zones retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "name": "Zone 1"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_zones()

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == 1

    @patch("requests.Session.request")
    def test_update_zone_success(self, mock_request):
        """Test successful zone update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "name": "Updated Zone",
        }
        mock_request.return_value = mock_response

        zone_data = {
            "name": "Updated Zone",
        }

        result = self.client.update_zone(123, zone_data)

        assert isinstance(result, dict)
        assert result["id"] == 123
        assert result["name"] == "Updated Zone"

    @patch("requests.Session.request")
    def test_get_campaign_statistics_success(self, mock_request):
        """Test successful campaign statistics retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"impressions": 1000, "clicks": 100}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_campaign_statistics(123)

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["impressions"] == 1000

    @patch("requests.Session.request")
    def test_get_slice_statistics_success(self, mock_request):
        """Test successful slice statistics retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"impressions": 500, "clicks": 50}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_slice_statistics(456)

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["impressions"] == 500

    @patch("requests.Session.request")
    def test_get_zone_statistics_success(self, mock_request):
        """Test successful zone statistics retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"impressions": 200, "clicks": 20}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_zone_statistics(789)

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["impressions"] == 200

    @patch("requests.Session.request")
    def test_get_creative_statistics_success(self, mock_request):
        """Test successful creative statistics retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"impressions": 100, "clicks": 10}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_creative_statistics(101)

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["impressions"] == 100

    @patch("requests.Session.request")
    def test_get_country_statistics_success(self, mock_request):
        """Test successful country statistics retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"impressions": 50, "clicks": 5}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_country_statistics("US")

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["impressions"] == 50

    @patch("requests.Session.request")
    def test_get_keyword_statistics_success(self, mock_request):
        """Test successful keyword statistics retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"impressions": 20, "clicks": 2}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_keyword_statistics("test")

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["impressions"] == 20

    @patch("requests.Session.request")
    def test_get_campaign_creatives_success(self, mock_request):
        """Test successful campaign creatives retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "name": "Creative 1"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_campaign_creatives(123)

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == 1

    @patch("requests.Session.request")
    def test_get_campaign_targeting_success(self, mock_request):
        """Test successful campaign targeting retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "countries": ["US"],
            "browsers": ["chrome"]
        }
        mock_request.return_value = mock_response

        result = self.client.get_campaign_targeting(123)

        assert isinstance(result, dict)
        assert "countries" in result
        assert len(result["countries"]) == 1

    @patch("requests.Session.request")
    def test_get_campaign_slices_success(self, mock_request):
        """Test successful campaign slices retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "name": "Slice 1"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_campaign_slices(123)

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == 1

    @patch("requests.Session.request")
    def test_get_campaign_zones_success(self, mock_request):
        """Test successful campaign zones retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "name": "Zone 1"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        result = self.client.get_campaign_zones(123)

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["id"] == 1

    @patch("requests.Session.request")
    def test_update_campaign_targeting_success(self, mock_request):
        """Test successful campaign targeting update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "countries": ["US", "CA"],
            "browsers": ["chrome", "firefox"]
        }
        mock_request.return_value = mock_response

        targeting_data = {
            "countries": ["US", "CA"],
            "browsers": ["chrome", "firefox"]
        }

        result = self.client.update_campaign_targeting(123, targeting_data)

        assert isinstance(result, dict)
        assert "countries" in result
        assert len(result["countries"]) == 2

    @patch("requests.Session.request")
    def test_update_campaign_slices_success(self, mock_request):
        """Test successful campaign slices update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "name": "Updated Slice"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        slices_data = {
            "result": [{"id": 1, "name": "Updated Slice"}]
        }

        result = self.client.update_campaign_slices(123, slices_data)

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["name"] == "Updated Slice"

    @patch("requests.Session.request")
    def test_update_campaign_zones_success(self, mock_request):
        """Test successful campaign zones update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"id": 1, "name": "Updated Zone"}],
            "total": 1
        }
        mock_request.return_value = mock_response

        zones_data = {
            "result": [{"id": 1, "name": "Updated Zone"}]
        }

        result = self.client.update_campaign_zones(123, zones_data)

        assert isinstance(result, dict)
        assert "result" in result
        assert len(result["result"]) == 1
        assert result["result"][0]["name"] == "Updated Zone"


class TestAsyncPropellerAdsClient:
    """Tests for the asynchronous client."""

    @pytest.mark.asyncio
    async def test_async_client_initialization(self):
        """Test async client initialization."""
        async with AsyncPropellerAdsClient(api_key="test_api_key") as client:
            assert client._sync_client.config.api_key == "test_api_key"
            assert hasattr(client, '_sync_client')

    @pytest.mark.asyncio
    @patch(
        'propellerads.client.PropellerAdsClient.get_balance',
        return_value=BalanceResponse(amount=1234.56)
    )
    async def test_get_balance_async_success(self, mock_get_balance):
        """Test successful async balance retrieval."""
        async with AsyncPropellerAdsClient(api_key="test_api_key") as client:
            result = await client.get_balance()
            assert isinstance(result, BalanceResponse)
            assert result.amount == Decimal("1234.56")

    @pytest.mark.asyncio
    @patch(
        'propellerads.client.PropellerAdsClient.get_campaigns',
        return_value={'result': [{'id': 1, 'name': 'Test Campaign'}]}
    )
    async def test_get_campaigns_async_success(self, mock_get_campaigns):
        """Test successful async campaign retrieval."""
        async with AsyncPropellerAdsClient(api_key="test_api_key") as client:
            result = await client.get_campaigns()
            assert isinstance(result, dict)
            assert 'result' in result
            assert len(result['result']) == 1

    @pytest.mark.asyncio
    @patch(
        'propellerads.client.PropellerAdsClient.get_statistics',
        return_value={'result': [{'date': '2025-09-30', 'impressions': 1000, 'clicks': 100}]}
    )
    async def test_get_statistics_async_success(self, mock_get_statistics):
        """Test successful async statistics retrieval."""
        async with AsyncPropellerAdsClient(api_key="test_api_key") as client:
            result = await client.get_statistics(date_from="2025-09-30 00:00:00", date_to="2025-09-30 23:59:59")
            assert isinstance(result, dict)
            assert 'result' in result
            assert len(result['result']) == 1
            assert result['result'][0]['impressions'] == 1000


@pytest.mark.integration
class TestRealAPI:
    """Integration tests with the real API."""

    def test_real_balance_check(self):
        """Test real balance retrieval."""
        if not os.getenv("MainAPI"):
            pytest.skip("MainAPI token not available")

        client = PropellerAdsClient(api_key=os.getenv("MainAPI"))
        result = client.get_balance()

        assert isinstance(result, BalanceResponse)
        assert result.amount >= 0

    def test_real_health_check(self):
        """Test real health check."""
        if not os.getenv("MainAPI"):
            pytest.skip("MainAPI token not available")

        client = PropellerAdsClient(api_key=os.getenv("MainAPI"))
        result = client.health_check()

        assert result["overall_status"] in ["healthy", "degraded", "unhealthy"]
        assert "balance" in result
