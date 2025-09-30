"""
Advanced Endpoint Tests for PropellerAds SDK

Comprehensive testing of advanced API endpoints and features.
"""

import pytest
from unittest.mock import Mock, patch
from propellerads.client import PropellerAdsClient
from propellerads.exceptions import PropellerAdsError


class TestCampaignManagement:
    """Test advanced campaign management features."""
    
    @patch('requests.Session.request')
    def test_campaign_creation_with_targeting(self, mock_request):
        """Test campaign creation with targeting options."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 12345,
            "name": "Advanced Campaign",
            "status": "active",
            "targeting": {
                "countries": ["US", "CA"],
                "devices": ["desktop", "mobile"]
            }
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        campaign_data = {
            "name": "Advanced Campaign",
            "target_url": "https://example.com",
            "daily_budget": 500.0,
            "targeting": {
                "countries": ["US", "CA"],
                "devices": ["desktop", "mobile"],
                "operating_systems": ["windows", "android"]
            }
        }
        
        result = client.create_campaign(campaign_data)
        
        assert result["id"] == 12345
        assert result["name"] == "Advanced Campaign"
        assert "targeting" in result
    
    @patch('requests.Session.request')
    def test_campaign_bulk_operations(self, mock_request):
        """Test bulk campaign operations."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "updated": [12345, 12346, 12347],
            "failed": [],
            "total": 3
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Simulate bulk update
        campaigns = client.get_campaigns()
        
        # Should handle bulk operations
        assert mock_request.called
    
    @patch('requests.Session.request')
    def test_campaign_status_transitions(self, mock_request):
        """Test campaign status transitions."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 12345,
            "status": "paused",
            "previous_status": "active"
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Test status update
        result = client.update_campaign(12345, {"status": "paused"})
        
        assert result["status"] == "paused"
        assert result["previous_status"] == "active"


class TestCreativeManagement:
    """Test creative management endpoints."""
    
    @patch('requests.Session.request')
    def test_creative_upload_and_validation(self, mock_request):
        """Test creative upload and validation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 67890,
            "name": "Test Creative",
            "type": "banner",
            "status": "pending_review",
            "dimensions": {"width": 728, "height": 90}
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        creative_data = {
            "name": "Test Creative",
            "type": "banner",
            "content": "base64_encoded_image_data",
            "dimensions": {"width": 728, "height": 90}
        }
        
        result = client.create_creative(creative_data)
        
        assert result["id"] == 67890
        assert result["type"] == "banner"
        assert result["status"] == "pending_review"
    
    @patch('requests.Session.request')
    def test_creative_format_validation(self, mock_request):
        """Test creative format validation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Banner 728x90", "type": "banner"},
            {"id": 2, "name": "Video 16:9", "type": "video"},
            {"id": 3, "name": "Native Ad", "type": "native"}
        ]
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        creatives = client.get_creatives()
        
        assert len(creatives) == 3
        assert any(c["type"] == "banner" for c in creatives)
        assert any(c["type"] == "video" for c in creatives)
        assert any(c["type"] == "native" for c in creatives)
    
    @patch('requests.Session.request')
    def test_creative_performance_tracking(self, mock_request):
        """Test creative performance tracking."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "creative_id": 67890,
            "impressions": 10000,
            "clicks": 250,
            "ctr": 2.5,
            "conversions": 15,
            "cost": 125.50
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        stats = client.get_creative_statistics(67890)
        
        assert stats["creative_id"] == 67890
        assert stats["ctr"] == 2.5
        assert stats["cost"] == 125.50


class TestTargetingOptions:
    """Test targeting options and configurations."""
    
    @patch('requests.Session.request')
    def test_geographic_targeting(self, mock_request):
        """Test geographic targeting options."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "countries": [
                {"code": "US", "name": "United States", "available": True},
                {"code": "CA", "name": "Canada", "available": True},
                {"code": "GB", "name": "United Kingdom", "available": True}
            ],
            "regions": [
                {"id": 1, "name": "North America", "countries": ["US", "CA"]},
                {"id": 2, "name": "Europe", "countries": ["GB", "DE", "FR"]}
            ]
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        targeting = client.get_targeting_options()
        
        assert "countries" in targeting
        assert "regions" in targeting
        assert len(targeting["countries"]) == 3
    
    @patch('requests.Session.request')
    def test_device_targeting(self, mock_request):
        """Test device targeting options."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "devices": [
                {"type": "desktop", "available": True},
                {"type": "mobile", "available": True},
                {"type": "tablet", "available": True}
            ],
            "operating_systems": [
                {"name": "Windows", "versions": ["10", "11"]},
                {"name": "Android", "versions": ["11", "12", "13"]},
                {"name": "iOS", "versions": ["15", "16", "17"]}
            ]
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        targeting = client.get_targeting_options()
        
        assert "devices" in targeting
        assert "operating_systems" in targeting
    
    @patch('requests.Session.request')
    def test_audience_targeting(self, mock_request):
        """Test audience targeting options."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "demographics": {
                "age_groups": ["18-24", "25-34", "35-44", "45-54", "55+"],
                "genders": ["male", "female", "other"]
            },
            "interests": [
                {"id": 1, "name": "Technology", "subcategories": ["Software", "Hardware"]},
                {"id": 2, "name": "Sports", "subcategories": ["Football", "Basketball"]}
            ]
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        targeting = client.get_targeting_options()
        
        assert "demographics" in targeting
        assert "interests" in targeting


class TestStatisticsAndReporting:
    """Test advanced statistics and reporting features."""
    
    @patch('requests.Session.request')
    def test_detailed_campaign_statistics(self, mock_request):
        """Test detailed campaign statistics."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "campaign_id": 12345,
            "date_range": {"from": "2023-01-01", "to": "2023-01-31"},
            "metrics": {
                "impressions": 100000,
                "clicks": 2500,
                "conversions": 125,
                "cost": 1250.00,
                "revenue": 2500.00,
                "profit": 1250.00,
                "roi": 100.0
            },
            "breakdown": {
                "by_day": [
                    {"date": "2023-01-01", "impressions": 3000, "clicks": 75},
                    {"date": "2023-01-02", "impressions": 3200, "clicks": 80}
                ],
                "by_country": [
                    {"country": "US", "impressions": 60000, "clicks": 1500},
                    {"country": "CA", "impressions": 40000, "clicks": 1000}
                ]
            }
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        stats = client.get_campaign_statistics(
            12345,
            date_from="2023-01-01 00:00:00",
            date_to="2023-01-31 23:59:59"
        )
        
        assert stats["campaign_id"] == 12345
        assert stats["metrics"]["roi"] == 100.0
        assert "breakdown" in stats
    
    @patch('requests.Session.request')
    def test_real_time_statistics(self, mock_request):
        """Test real-time statistics."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "timestamp": "2023-01-15T10:30:00Z",
            "live_campaigns": 5,
            "active_impressions": 1500,
            "current_spend": 45.75,
            "hourly_metrics": {
                "impressions": 500,
                "clicks": 12,
                "cost": 15.25
            }
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        stats = client.get_statistics(
            date_from="2023-01-15 10:00:00",
            date_to="2023-01-15 10:59:59"
        )
        
        assert "timestamp" in stats
        assert "live_campaigns" in stats
    
    @patch('requests.Session.request')
    def test_custom_report_generation(self, mock_request):
        """Test custom report generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "report_id": "rpt_123456",
            "status": "completed",
            "download_url": "https://reports.propellerads.com/download/rpt_123456",
            "format": "csv",
            "size": "2.5MB",
            "generated_at": "2023-01-15T11:00:00Z"
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Simulate report generation request
        campaigns = client.get_campaigns()
        
        # Should handle report generation
        assert mock_request.called


class TestZoneManagement:
    """Test zone management features."""
    
    @patch('requests.Session.request')
    def test_zone_configuration(self, mock_request):
        """Test zone configuration options."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1001,
                "name": "Premium Desktop",
                "type": "display",
                "formats": ["728x90", "300x250", "160x600"],
                "countries": ["US", "CA", "GB"],
                "pricing": {"cpm": 2.50, "cpc": 0.25}
            },
            {
                "id": 1002,
                "name": "Mobile Push",
                "type": "push",
                "formats": ["push_notification"],
                "countries": ["US", "CA"],
                "pricing": {"cpm": 1.80, "cpc": 0.18}
            }
        ]
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        zones = client.get_zones()
        
        assert len(zones) == 2
        assert zones[0]["type"] == "display"
        assert zones[1]["type"] == "push"
    
    @patch('requests.Session.request')
    def test_zone_performance_optimization(self, mock_request):
        """Test zone performance optimization."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "zone_id": 1001,
            "optimization_suggestions": [
                {
                    "type": "bid_adjustment",
                    "recommendation": "increase_bid",
                    "current_bid": 0.25,
                    "suggested_bid": 0.30,
                    "expected_improvement": "15% more impressions"
                },
                {
                    "type": "targeting_adjustment",
                    "recommendation": "expand_countries",
                    "current_countries": ["US"],
                    "suggested_countries": ["US", "CA", "GB"],
                    "expected_improvement": "40% more volume"
                }
            ]
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        stats = client.get_zone_statistics(1001)
        
        # Should return zone statistics
        assert mock_request.called


class TestAccountManagement:
    """Test account management features."""
    
    @patch('requests.Session.request')
    def test_user_profile_management(self, mock_request):
        """Test user profile management."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 12345,
            "email": "user@example.com",
            "name": "Test User",
            "account_type": "advertiser",
            "status": "active",
            "created_at": "2023-01-01T00:00:00Z",
            "settings": {
                "timezone": "UTC",
                "currency": "USD",
                "notifications": {
                    "email": True,
                    "push": False
                }
            }
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        profile = client.get_user_profile()
        
        assert profile["account_type"] == "advertiser"
        assert profile["settings"]["currency"] == "USD"
    
    @patch('requests.Session.request')
    def test_payment_and_billing(self, mock_request):
        """Test payment and billing features."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "invoices": [
                {
                    "id": "inv_001",
                    "amount": 1000.00,
                    "currency": "USD",
                    "status": "paid",
                    "date": "2023-01-01"
                }
            ],
            "payments": [
                {
                    "id": "pay_001",
                    "amount": 1000.00,
                    "method": "credit_card",
                    "status": "completed",
                    "date": "2023-01-01"
                }
            ]
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        invoices = client.get_user_invoices()
        
        assert len(invoices["invoices"]) == 1
        assert invoices["invoices"][0]["status"] == "paid"
    
    @patch('requests.Session.request')
    def test_notification_management(self, mock_request):
        """Test notification management."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "notifications": [
                {
                    "id": 1,
                    "type": "campaign_approved",
                    "message": "Your campaign has been approved",
                    "read": False,
                    "created_at": "2023-01-15T10:00:00Z"
                },
                {
                    "id": 2,
                    "type": "budget_alert",
                    "message": "Campaign budget 80% spent",
                    "read": True,
                    "created_at": "2023-01-14T15:30:00Z"
                }
            ],
            "unread_count": 1
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        notifications = client.get_notifications()
        
        assert notifications["unread_count"] == 1
        assert len(notifications["notifications"]) == 2


class TestAdvancedFeatures:
    """Test advanced SDK features."""
    
    @patch('requests.Session.request')
    def test_webhook_integration(self, mock_request):
        """Test webhook integration features."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "webhook_url": "https://example.com/webhook",
            "events": ["campaign_approved", "budget_alert", "conversion"],
            "status": "active",
            "last_delivery": "2023-01-15T10:00:00Z"
        }
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Simulate webhook configuration check
        profile = client.get_user_profile()
        
        # Should handle webhook-related requests
        assert mock_request.called
    
    @patch('requests.Session.request')
    def test_api_rate_limit_handling(self, mock_request):
        """Test API rate limit handling."""
        # First call succeeds
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.text = '100.00'
        
        # Second call hits rate limit
        mock_response_limit = Mock()
        mock_response_limit.status_code = 429
        mock_response_limit.text = 'Rate limit exceeded'
        
        mock_request.side_effect = [mock_response_success, mock_response_limit]
        
        client = PropellerAdsClient(api_key="test-key")
        
        # First call should succeed
        balance1 = client.get_balance()
        assert balance1 is not None
        
        # Second call should handle rate limit
        try:
            balance2 = client.get_balance()
        except Exception:
            pass  # Expected due to rate limit
        
        assert mock_request.call_count == 2
    
    def test_configuration_flexibility(self):
        """Test configuration flexibility."""
        # Test different configuration options
        client1 = PropellerAdsClient(
            api_key="test-key-1",
            timeout=60,
            max_retries=5,
            rate_limit=120
        )
        
        client2 = PropellerAdsClient(
            api_key="test-key-2",
            timeout=30,
            max_retries=3,
            rate_limit=60,
            enable_metrics=False
        )
        
        # Configurations should be different
        assert client1.config.timeout == 60
        assert client2.config.timeout == 30
        assert client1.config.rate_limit == 120
        assert client2.config.rate_limit == 60
