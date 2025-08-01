"""
Performance Tests for Seraaj API
Tests response times, throughput, and system behavior under load
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi.testclient import TestClient
from sqlmodel import Session
from models import User, Opportunity
from tests.conftest import TestDataFactory


@pytest.mark.performance
class TestAPIPerformance:
    """Test API endpoint performance"""

    def test_opportunity_list_response_time(
        self,
        client: TestClient,
        session: Session,
        test_user_organization: User,
        performance_timer,
    ):
        """Test opportunities list endpoint response time"""
        # Create test data
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=100
        )

        performance_timer.start()
        response = client.get("/v1/opportunities")
        performance_timer.stop()

        assert response.status_code == 200
        assert performance_timer.elapsed < 2.0  # Should respond within 2 seconds

        data = response.json()
        assert len(data["opportunities"]) > 0

    def test_opportunity_search_performance(
        self,
        client: TestClient,
        session: Session,
        test_user_organization: User,
        performance_timer,
    ):
        """Test search endpoint performance with large dataset"""
        # Create diverse opportunities
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=200
        )

        search_queries = [
            "q=programming",
            "skills=Programming&category=Technology",
            "location=Test City&is_remote=true",
            "q=volunteer&sort=created_date",
        ]

        for query in search_queries:
            performance_timer.start()
            response = client.get(f"/v1/opportunities/search?{query}")
            performance_timer.stop()

            assert response.status_code == 200
            assert performance_timer.elapsed < 3.0  # Should respond within 3 seconds

    def test_user_authentication_performance(
        self, client: TestClient, performance_timer
    ):
        """Test authentication endpoint performance"""
        # Register user first
        registration_data = {
            "email": "perf_test@example.com",
            "password": "testpassword123",
            "first_name": "Performance",
            "last_name": "Test",
            "role": "volunteer",
        }
        client.post("/v1/auth/register", json=registration_data)

        # Test login performance
        login_data = {
            "username": "perf_test@example.com",
            "password": "testpassword123",
        }

        performance_timer.start()
        response = client.post("/v1/auth/login", data=login_data)
        performance_timer.stop()

        assert response.status_code == 200
        assert performance_timer.elapsed < 1.0  # Should respond within 1 second

    def test_opportunity_creation_performance(
        self, client: TestClient, auth_headers_organization: dict, performance_timer
    ):
        """Test opportunity creation performance"""
        opportunity_data = {
            "title": "Performance Test Opportunity",
            "description": "Testing opportunity creation performance",
            "skills_required": ["Programming"],
            "location": "Test City",
            "time_commitment": "5 hours/week",
            "volunteers_needed": 3,
            "category": "Technology",
        }

        performance_timer.start()
        response = client.post(
            "/v1/opportunities",
            json=opportunity_data,
            headers=auth_headers_organization,
        )
        performance_timer.stop()

        assert response.status_code == 201
        assert performance_timer.elapsed < 1.5  # Should respond within 1.5 seconds


@pytest.mark.performance
class TestConcurrentUsers:
    """Test system behavior with concurrent users"""

    def test_concurrent_opportunity_browsing(
        self, client: TestClient, session: Session, test_user_organization: User
    ):
        """Test multiple users browsing opportunities simultaneously"""
        # Create test data
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=50
        )

        def browse_opportunities():
            start_time = time.time()
            response = client.get("/v1/opportunities")
            end_time = time.time()

            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "data_count": len(response.json().get("opportunities", [])),
            }

        # Simulate 20 concurrent users
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(browse_opportunities) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]

        # All requests should succeed
        assert all(result["status_code"] == 200 for result in results)

        # Average response time should be reasonable
        avg_response_time = sum(result["response_time"] for result in results) / len(
            results
        )
        assert avg_response_time < 3.0

        # All should return data
        assert all(result["data_count"] > 0 for result in results)

    def test_concurrent_user_registration(self, client: TestClient):
        """Test concurrent user registrations"""

        def register_user(user_index):
            registration_data = {
                "email": f"concurrent_user_{user_index}@test.com",
                "password": "testpassword123",
                "first_name": f"User{user_index}",
                "last_name": "Test",
                "role": "volunteer",
            }

            start_time = time.time()
            response = client.post("/v1/auth/register", json=registration_data)
            end_time = time.time()

            return {
                "user_index": user_index,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
            }

        # Register 10 users concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(register_user, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]

        # All registrations should succeed
        success_count = sum(1 for result in results if result["status_code"] == 201)
        assert success_count >= 8  # Allow for some potential conflicts

        # Response times should be reasonable
        avg_response_time = sum(result["response_time"] for result in results) / len(
            results
        )
        assert avg_response_time < 2.0

    def test_concurrent_application_submissions(
        self,
        client: TestClient,
        session: Session,
        test_opportunity: Opportunity,
        sample_application_data: dict,
    ):
        """Test concurrent application submissions"""
        # Make opportunity active
        test_opportunity.status = "active"
        test_opportunity.volunteers_needed = 20  # Allow many applications
        session.add(test_opportunity)
        session.commit()

        def submit_application(volunteer_index):
            # Register volunteer
            registration_data = {
                "email": f"applicant_{volunteer_index}@test.com",
                "password": "testpassword123",
                "first_name": f"Applicant{volunteer_index}",
                "last_name": "Test",
                "role": "volunteer",
            }

            register_response = client.post("/v1/auth/register", json=registration_data)
            if register_response.status_code != 201:
                return {"success": False, "error": "Registration failed"}

            token = register_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Submit application
            application_data = {
                "opportunity_id": test_opportunity.id,
                **sample_application_data,
            }

            start_time = time.time()
            response = client.post(
                "/v1/applications", json=application_data, headers=headers
            )
            end_time = time.time()

            return {
                "volunteer_index": volunteer_index,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code
                in [201, 400],  # 400 might be duplicate application
            }

        # Submit 15 applications concurrently
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(submit_application, i) for i in range(15)]
            results = [future.result() for future in as_completed(futures)]

        # Most applications should succeed
        success_count = sum(1 for result in results if result.get("success", False))
        assert success_count >= 10

        # Response times should be reasonable
        valid_results = [r for r in results if "response_time" in r]
        if valid_results:
            avg_response_time = sum(
                result["response_time"] for result in valid_results
            ) / len(valid_results)
            assert avg_response_time < 3.0


@pytest.mark.performance
class TestDatabasePerformance:
    """Test database operation performance"""

    def test_large_dataset_query_performance(
        self,
        client: TestClient,
        session: Session,
        test_user_organization: User,
        performance_timer,
    ):
        """Test query performance with large datasets"""
        # Create large dataset
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=500
        )
        TestDataFactory.create_multiple_volunteers(session, count=100)

        # Test various queries
        queries = [
            "/v1/opportunities",
            "/v1/opportunities?category=Technology",
            "/v1/opportunities/search?q=programming",
            "/v1/opportunities?is_remote=true&limit=50",
        ]

        for query in queries:
            performance_timer.start()
            response = client.get(query)
            performance_timer.stop()

            assert response.status_code == 200
            assert performance_timer.elapsed < 5.0  # Should respond within 5 seconds

    def test_pagination_performance(
        self,
        client: TestClient,
        session: Session,
        test_user_organization: User,
        performance_timer,
    ):
        """Test pagination performance with large datasets"""
        # Create large dataset
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=1000
        )

        # Test different page sizes and offsets
        test_cases = [
            {"skip": 0, "limit": 10},
            {"skip": 100, "limit": 20},
            {"skip": 500, "limit": 50},
            {"skip": 900, "limit": 100},
        ]

        for case in test_cases:
            performance_timer.start()
            response = client.get(
                f"/v1/opportunities?skip={case['skip']}&limit={case['limit']}"
            )
            performance_timer.stop()

            assert response.status_code == 200
            assert performance_timer.elapsed < 2.0  # Should respond within 2 seconds

            data = response.json()
            assert len(data["opportunities"]) <= case["limit"]


@pytest.mark.performance
class TestMemoryAndResourceUsage:
    """Test memory usage and resource consumption"""

    def test_memory_usage_with_large_responses(
        self, client: TestClient, session: Session, test_user_organization: User
    ):
        """Test memory usage when returning large datasets"""
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create large dataset
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=200
        )

        # Make multiple large requests
        for _ in range(10):
            response = client.get("/v1/opportunities?limit=100")
            assert response.status_code == 200

        # Check memory usage didn't grow excessively
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024  # 100MB

    def test_file_upload_performance(
        self, client: TestClient, auth_headers_volunteer: dict, performance_timer
    ):
        """Test file upload performance"""
        # Create mock large file (1MB)
        large_file_content = b"x" * (1024 * 1024)

        file_data = {"file": ("large_file.txt", large_file_content, "text/plain")}
        form_data = {
            "upload_category": "document",
            "file_description": "Performance test file",
        }

        performance_timer.start()
        response = client.post(
            "/v1/files/upload",
            files=file_data,
            data=form_data,
            headers=auth_headers_volunteer,
        )
        performance_timer.stop()

        # Should handle large file upload reasonably fast
        assert performance_timer.elapsed < 10.0  # Within 10 seconds
        assert response.status_code in [201, 400, 413]  # 413 = file too large


@pytest.mark.performance
class TestCachePerformance:
    """Test caching and performance optimizations"""

    def test_repeated_requests_performance(
        self, client: TestClient, session: Session, test_user_organization: User
    ):
        """Test that repeated requests are optimized (caching, etc.)"""
        # Create test data
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=100
        )

        # Make first request (cold)
        start_time = time.time()
        first_response = client.get("/v1/opportunities")
        first_time = time.time() - start_time

        # Make subsequent requests (should be faster if cached)
        response_times = []
        for _ in range(5):
            start_time = time.time()
            response = client.get("/v1/opportunities")
            response_time = time.time() - start_time
            response_times.append(response_time)

            assert response.status_code == 200

        # Subsequent requests should be consistently fast
        avg_subsequent_time = sum(response_times) / len(response_times)

        # This test assumes some level of caching/optimization
        # If no caching is implemented, this might need adjustment
        assert avg_subsequent_time <= first_time * 1.5  # Allow some variance

    def test_search_index_performance(
        self,
        client: TestClient,
        session: Session,
        test_user_organization: User,
        performance_timer,
    ):
        """Test search performance assumes proper indexing"""
        # Create large searchable dataset
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=300
        )

        # Test various search queries
        search_terms = [
            "programming",
            "education",
            "technology",
            "volunteer",
            "community",
        ]

        for term in search_terms:
            performance_timer.start()
            response = client.get(f"/v1/opportunities/search?q={term}")
            performance_timer.stop()

            assert response.status_code == 200
            # Search should be fast even with large dataset
            assert performance_timer.elapsed < 2.0


@pytest.mark.performance
class TestLoadTesting:
    """Basic load testing scenarios"""

    def test_sustained_load_simulation(
        self, client: TestClient, session: Session, test_user_organization: User
    ):
        """Test system behavior under sustained load"""
        # Create test data
        TestDataFactory.create_multiple_opportunities(
            session, test_user_organization, count=100
        )

        def make_request():
            start_time = time.time()
            response = client.get("/v1/opportunities")
            end_time = time.time()

            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
            }

        # Simulate sustained load for 30 seconds with 5 concurrent users
        results = []
        end_time = time.time() + 30  # Run for 30 seconds

        with ThreadPoolExecutor(max_workers=5) as executor:
            while time.time() < end_time:
                future = executor.submit(make_request)
                results.append(future.result())
                time.sleep(0.1)  # Small delay between requests

        # Analyze results
        success_rate = sum(1 for r in results if r["status_code"] == 200) / len(results)
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        max_response_time = max(r["response_time"] for r in results)

        # System should maintain good performance under sustained load
        assert success_rate >= 0.95  # 95% success rate
        assert avg_response_time < 2.0  # Average response time under 2 seconds
        assert max_response_time < 10.0  # No response should take more than 10 seconds

        print(
            f"Load test results: {len(results)} requests, {success_rate:.2%} success rate, "
            f"{avg_response_time:.2f}s avg response time, {max_response_time:.2f}s max response time"
        )
