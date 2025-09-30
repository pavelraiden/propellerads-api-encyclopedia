"""
Integration and Workflow Tests for PropellerAds SDK

Comprehensive end-to-end tests for complete workflows,
integration scenarios, and real-world usage patterns.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock, call
from propellerads import PropellerAdsClient
from propellerads.exceptions import PropellerAdsError, AuthenticationError, RateLimitError


class TestCampaignLifecycle:
    """Test complete campaign lifecycle workflows."""
    
    @patch('requests.Session.request')
    def test_complete_campaign_creation_workflow(self, mock_request):
        """Test complete campaign creation workflow."""
        # Mock responses for different stages
        responses = [
            # Balance check
            Mock(status_code=200, text='1000.00'),
            # Campaign creation
            Mock(status_code=201, json=lambda: {"id": 123, "name": "Test Campaign"}),
            # Campaign details verification
            Mock(status_code=200, json=lambda: {"id": 123, "name": "Test Campaign", "status": 1}),
            # Campaign activation
            Mock(status_code=200, json=lambda: {"id": 123, "status": 6})
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Step 1: Check balance
        balance = client.get_balance()
        assert float(balance.amount) >= 100.0
        
        # Step 2: Create campaign
        campaign_data = {
            "name": "Test Campaign",
            "target_url": "https://example.com",
            "daily_budget": 100.0
        }
        campaign = client.create_campaign(campaign_data)
        assert campaign["id"] == 123
        
        # Step 3: Verify campaign details
        details = client.get_campaign_details(123)
        assert details["id"] == 123
        assert details["name"] == "Test Campaign"
        
        # Step 4: Activate campaign
        updated = client.update_campaign(123, {"status": "active"})
        assert updated["status"] == 6
        
        # Verify all calls were made
        assert mock_request.call_count == 4
    
    @patch('requests.Session.request')
    def test_campaign_optimization_workflow(self, mock_request):
        """Test campaign optimization workflow."""
        # Mock responses
        responses = [
            # Get campaigns
            Mock(status_code=200, json=lambda: [
                {"id": 1, "name": "Campaign 1", "status": 6, "clicks": 100, "conversions": 5},
                {"id": 2, "name": "Campaign 2", "status": 6, "clicks": 50, "conversions": 1}
            ]),
            # Get statistics for campaign 1
            Mock(status_code=200, json=lambda: {
                "clicks": 100, "impressions": 1000, "conversions": 5, "cost": 50.0
            }),
            # Get statistics for campaign 2
            Mock(status_code=200, json=lambda: {
                "clicks": 50, "impressions": 800, "conversions": 1, "cost": 30.0
            }),
            # Update budget for best performing campaign
            Mock(status_code=200, json=lambda: {"id": 1, "daily_budget": 150.0}),
            # Pause poor performing campaign
            Mock(status_code=200, json=lambda: {"id": 2, "status": 7})
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Step 1: Get all campaigns
        campaigns = client.get_campaigns()
        assert len(campaigns) == 2
        
        # Step 2: Analyze performance
        best_campaign = None
        worst_campaign = None
        best_conversion_rate = 0
        worst_conversion_rate = float('inf')
        
        for campaign in campaigns:
            stats = client.get_statistics(campaign_id=campaign["id"])
            conversion_rate = stats["conversions"] / stats["clicks"] if stats["clicks"] > 0 else 0
            
            if conversion_rate > best_conversion_rate:
                best_conversion_rate = conversion_rate
                best_campaign = campaign
            
            if conversion_rate < worst_conversion_rate:
                worst_conversion_rate = conversion_rate
                worst_campaign = campaign
        
        # Step 3: Optimize - increase budget for best, pause worst
        if best_campaign:
            client.update_campaign(best_campaign["id"], {"daily_budget": 150.0})
        
        if worst_campaign and worst_conversion_rate < 0.02:  # Less than 2% conversion rate
            client.update_campaign(worst_campaign["id"], {"status": "paused"})
        
        assert mock_request.call_count == 5
    
    @patch('requests.Session.request')
    def test_bulk_campaign_management_workflow(self, mock_request):
        """Test bulk campaign management workflow."""
        # Mock responses for bulk operations
        campaign_list = [{"id": i, "name": f"Campaign {i}", "status": 6} for i in range(1, 11)]
        
        responses = [
            # Get campaigns
            Mock(status_code=200, json=lambda: campaign_list),
            # Bulk status updates (10 campaigns)
            *[Mock(status_code=200, json=lambda i=i: {"id": i, "status": 7}) for i in range(1, 11)]
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Step 1: Get all campaigns
        campaigns = client.get_campaigns()
        assert len(campaigns) == 10
        
        # Step 2: Bulk pause all campaigns
        updated_campaigns = []
        for campaign in campaigns:
            updated = client.update_campaign(campaign["id"], {"status": "paused"})
            updated_campaigns.append(updated)
        
        # Verify all campaigns were updated
        assert len(updated_campaigns) == 10
        for updated in updated_campaigns:
            assert updated["status"] == 7  # Paused
        
        assert mock_request.call_count == 11  # 1 list + 10 updates


class TestErrorRecoveryWorkflows:
    """Test error recovery and resilience workflows."""
    
    @patch('requests.Session.request')
    def test_retry_on_temporary_failure_workflow(self, mock_request):
        """Test retry workflow on temporary failures."""
        # First two calls fail, third succeeds
        responses = [
            Mock(status_code=500, text="Internal Server Error"),
            Mock(status_code=503, text="Service Unavailable"),
            Mock(status_code=200, text='100.00')
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key", max_retries=3)
        
        # Should eventually succeed after retries
        balance = client.get_balance()
        assert float(balance.amount) == 100.0
        
        # Should have made 3 attempts
        assert mock_request.call_count == 3
    
    @patch('requests.Session.request')
    def test_circuit_breaker_recovery_workflow(self, mock_request):
        """Test circuit breaker recovery workflow."""
        # Simulate failures to trigger circuit breaker
        failure_responses = [Mock(status_code=500, text="Error") for _ in range(6)]
        success_response = Mock(status_code=200, text='100.00')
        
        mock_request.side_effect = failure_responses + [success_response]
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Make requests to trigger circuit breaker
        for _ in range(6):
            try:
                client.get_balance()
            except PropellerAdsError:
                pass
        
        # Circuit should be open now
        assert client.circuit_breaker['state'] == 'open'
        
        # Wait for recovery timeout
        client.circuit_breaker['last_failure'] = time.time() - 70
        
        # Next request should succeed (circuit recovery)
        balance = client.get_balance()
        assert float(balance.amount) == 100.0
        assert client.circuit_breaker['state'] == 'closed'
    
    @patch('requests.Session.request')
    def test_rate_limit_recovery_workflow(self, mock_request):
        """Test rate limit recovery workflow."""
        # First request hits rate limit, second succeeds
        responses = [
            Mock(status_code=429, text="Rate limit exceeded", headers={'Retry-After': '1'}),
            Mock(status_code=200, text='100.00')
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # First request should fail with rate limit
        with pytest.raises(RateLimitError):
            client.get_balance()
        
        # Wait and retry should succeed
        time.sleep(0.1)  # Brief wait for test
        balance = client.get_balance()
        assert float(balance.amount) == 100.0


class TestDataConsistencyWorkflows:
    """Test data consistency across operations."""
    
    @patch('requests.Session.request')
    def test_campaign_data_consistency_workflow(self, mock_request):
        """Test data consistency across campaign operations."""
        campaign_data = {
            "id": 123,
            "name": "Consistent Campaign",
            "daily_budget": 100.0,
            "status": 6
        }
        
        responses = [
            # Create campaign
            Mock(status_code=201, json=lambda: campaign_data),
            # Get campaign details
            Mock(status_code=200, json=lambda: campaign_data),
            # Update campaign
            Mock(status_code=200, json=lambda: {**campaign_data, "daily_budget": 150.0}),
            # Get updated details
            Mock(status_code=200, json=lambda: {**campaign_data, "daily_budget": 150.0})
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Create campaign
        created = client.create_campaign({
            "name": "Consistent Campaign",
            "target_url": "https://example.com",
            "daily_budget": 100.0
        })
        
        # Verify creation
        details = client.get_campaign_details(created["id"])
        assert details["name"] == created["name"]
        assert details["daily_budget"] == created["daily_budget"]
        
        # Update campaign
        updated = client.update_campaign(created["id"], {"daily_budget": 150.0})
        
        # Verify update
        updated_details = client.get_campaign_details(created["id"])
        assert updated_details["daily_budget"] == 150.0
        assert updated_details["name"] == created["name"]  # Unchanged fields preserved
    
    @patch('requests.Session.request')
    def test_statistics_consistency_workflow(self, mock_request):
        """Test statistics consistency across different endpoints."""
        base_stats = {
            "clicks": 100,
            "impressions": 1000,
            "conversions": 5,
            "cost": 50.0
        }
        
        responses = [
            # Campaign statistics
            Mock(status_code=200, json=lambda: base_stats),
            # Overall statistics
            Mock(status_code=200, json=lambda: {
                "campaigns": [{"id": 123, **base_stats}],
                "totals": base_stats
            }),
            # Date-range statistics
            Mock(status_code=200, json=lambda: {
                "2023-01-01": base_stats
            })
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Get campaign-specific stats
        campaign_stats = client.get_statistics(campaign_id=123)
        
        # Get overall stats
        overall_stats = client.get_statistics()
        
        # Get date-range stats
        date_stats = client.get_statistics(
            date_from="2023-01-01",
            date_to="2023-01-01"
        )
        
        # Verify consistency
        assert campaign_stats["clicks"] == overall_stats["totals"]["clicks"]
        assert campaign_stats["clicks"] == date_stats["2023-01-01"]["clicks"]


class TestPerformanceWorkflows:
    """Test performance-critical workflows."""
    
    @patch('requests.Session.request')
    def test_high_frequency_monitoring_workflow(self, mock_request):
        """Test high-frequency monitoring workflow."""
        # Mock consistent responses
        mock_response = Mock(status_code=200, text='100.00')
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key", rate_limit=120)  # 2 per second
        
        # Simulate monitoring loop
        start_time = time.time()
        successful_checks = 0
        
        for _ in range(10):
            try:
                balance = client.get_balance()
                successful_checks += 1
            except RateLimitError:
                time.sleep(0.1)  # Brief pause on rate limit
            except Exception:
                pass
        
        total_time = time.time() - start_time
        
        # Should complete monitoring efficiently
        assert successful_checks >= 8  # Allow some rate limiting
        assert total_time < 2.0  # Should be fast
    
    @patch('requests.Session.request')
    def test_batch_processing_workflow(self, mock_request):
        """Test batch processing workflow."""
        # Mock responses for batch operations
        campaign_responses = [
            Mock(status_code=200, json=lambda i=i: {"id": i, "name": f"Campaign {i}"})
            for i in range(1, 21)  # 20 campaigns
        ]
        mock_request.side_effect = campaign_responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Batch process campaigns
        start_time = time.time()
        processed_campaigns = []
        
        for i in range(1, 21):
            campaign = client.get_campaign_details(i)
            processed_campaigns.append(campaign)
        
        processing_time = time.time() - start_time
        
        # Should process batch efficiently
        assert len(processed_campaigns) == 20
        assert processing_time < 5.0  # Should complete in reasonable time
    
    @patch('requests.Session.request')
    def test_concurrent_workflow_handling(self, mock_request):
        """Test handling of concurrent workflows."""
        import threading
        
        mock_response = Mock(status_code=200, text='100.00')
        mock_request.return_value = mock_response
        
        client = PropellerAdsClient(api_key="test-key")
        results = []
        errors = []
        
        def workflow_task():
            try:
                # Simulate a workflow
                balance = client.get_balance()
                results.append(balance)
            except Exception as e:
                errors.append(e)
        
        # Run multiple workflows concurrently
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=workflow_task)
            threads.append(thread)
        
        start_time = time.time()
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # All workflows should succeed
        assert len(errors) == 0
        assert len(results) == 5
        assert total_time < 1.0


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    @patch('requests.Session.request')
    def test_daily_optimization_scenario(self, mock_request):
        """Test daily optimization scenario."""
        # Mock data for daily optimization
        responses = [
            # Get campaigns
            Mock(status_code=200, json=lambda: [
                {"id": 1, "name": "Campaign 1", "daily_budget": 100.0, "status": 6},
                {"id": 2, "name": "Campaign 2", "daily_budget": 50.0, "status": 6}
            ]),
            # Get yesterday's statistics
            Mock(status_code=200, json=lambda: {
                "campaigns": [
                    {"id": 1, "clicks": 200, "conversions": 10, "cost": 80.0},
                    {"id": 2, "clicks": 50, "conversions": 1, "cost": 40.0}
                ]
            }),
            # Update budget for campaign 1
            Mock(status_code=200, json=lambda: {"id": 1, "daily_budget": 120.0}),
            # Pause campaign 2
            Mock(status_code=200, json=lambda: {"id": 2, "status": 7})
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Daily optimization workflow
        campaigns = client.get_campaigns()
        yesterday_stats = client.get_statistics(
            date_from="2023-01-01",
            date_to="2023-01-01"
        )
        
        # Analyze and optimize
        for campaign in campaigns:
            campaign_stats = next(
                (s for s in yesterday_stats["campaigns"] if s["id"] == campaign["id"]),
                None
            )
            
            if campaign_stats:
                conversion_rate = campaign_stats["conversions"] / campaign_stats["clicks"]
                cost_per_conversion = campaign_stats["cost"] / campaign_stats["conversions"]
                
                if conversion_rate > 0.04 and cost_per_conversion < 10:
                    # Good performance - increase budget
                    new_budget = campaign["daily_budget"] * 1.2
                    client.update_campaign(campaign["id"], {"daily_budget": new_budget})
                elif conversion_rate < 0.02:
                    # Poor performance - pause
                    client.update_campaign(campaign["id"], {"status": "paused"})
        
        assert mock_request.call_count == 4
    
    @patch('requests.Session.request')
    def test_emergency_pause_scenario(self, mock_request):
        """Test emergency pause scenario."""
        # Mock responses for emergency scenario
        responses = [
            # Get balance - low balance detected
            Mock(status_code=200, text='10.00'),
            # Get active campaigns
            Mock(status_code=200, json=lambda: [
                {"id": 1, "name": "Campaign 1", "status": 6, "daily_budget": 100.0},
                {"id": 2, "name": "Campaign 2", "status": 6, "daily_budget": 50.0},
                {"id": 3, "name": "Campaign 3", "status": 7, "daily_budget": 75.0}  # Already paused
            ]),
            # Pause campaign 1
            Mock(status_code=200, json=lambda: {"id": 1, "status": 7}),
            # Pause campaign 2
            Mock(status_code=200, json=lambda: {"id": 2, "status": 7})
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Emergency workflow
        balance = client.get_balance()
        
        if float(balance.amount) < 50.0:  # Emergency threshold
            campaigns = client.get_campaigns()
            
            # Pause all active campaigns
            for campaign in campaigns:
                if campaign["status"] == 6:  # Active
                    client.update_campaign(campaign["id"], {"status": "paused"})
        
        assert mock_request.call_count == 4
    
    @patch('requests.Session.request')
    def test_scaling_workflow_scenario(self, mock_request):
        """Test campaign scaling workflow scenario."""
        # Mock responses for scaling workflow
        responses = [
            # Get top performing campaigns
            Mock(status_code=200, json=lambda: [
                {"id": 1, "name": "Top Campaign", "daily_budget": 100.0, "status": 6}
            ]),
            # Get performance data
            Mock(status_code=200, json=lambda: {
                "clicks": 500, "conversions": 25, "cost": 80.0, "revenue": 250.0
            }),
            # Scale up budget
            Mock(status_code=200, json=lambda: {"id": 1, "daily_budget": 200.0}),
            # Create similar campaign
            Mock(status_code=201, json=lambda: {"id": 2, "name": "Scaled Campaign"}),
            # Verify new campaign
            Mock(status_code=200, json=lambda: {"id": 2, "name": "Scaled Campaign", "status": 1})
        ]
        mock_request.side_effect = responses
        
        client = PropellerAdsClient(api_key="test-key")
        
        # Scaling workflow
        top_campaigns = client.get_campaigns()  # Assume filtered for top performers
        
        for campaign in top_campaigns:
            stats = client.get_statistics(campaign_id=campaign["id"])
            
            # Check if profitable and scalable
            roi = stats["revenue"] / stats["cost"] if stats["cost"] > 0 else 0
            conversion_rate = stats["conversions"] / stats["clicks"] if stats["clicks"] > 0 else 0
            
            if roi > 2.0 and conversion_rate > 0.04:
                # Scale up existing campaign
                new_budget = campaign["daily_budget"] * 2
                client.update_campaign(campaign["id"], {"daily_budget": new_budget})
                
                # Create duplicate campaign for further scaling
                new_campaign_data = {
                    "name": f"Scaled {campaign['name']}",
                    "target_url": "https://example.com",
                    "daily_budget": campaign["daily_budget"]
                }
                new_campaign = client.create_campaign(new_campaign_data)
                
                # Verify creation
                client.get_campaign_details(new_campaign["id"])
        
        assert mock_request.call_count == 5
