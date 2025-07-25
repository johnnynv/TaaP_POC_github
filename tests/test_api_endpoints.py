"""API endpoint tests for cloud native testing platform."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.api_client import APIClient, APIResponse
from src.config import Config


class TestUserAPIEndpoints:
    """Test user-related API endpoints (20 tests)."""
    
    @pytest.mark.api
    async def test_get_user_success(self, api_client, sample_user_data):
        """Test successful user retrieval."""
        user_id = sample_user_data["id"]
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data=sample_user_data,
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get(f"/users/{user_id}")
            assert response.success
            assert response.status_code == 200
            assert response.data["id"] == user_id

    @pytest.mark.api
    async def test_get_user_not_found(self, api_client):
        """Test user not found scenario."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=404,
                data={"error": "User not found"},
                headers={},
                response_time=0.1,
                success=False
            )
            
            response = await api_client.get("/users/nonexistent")
            assert not response.success
            assert response.status_code == 404

    @pytest.mark.api
    async def test_create_user_success(self, api_client, sample_user_data):
        """Test successful user creation."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=201,
                data=sample_user_data,
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post("/users", data=sample_user_data)
            assert response.success
            assert response.status_code == 201

    @pytest.mark.api
    async def test_create_user_validation_error(self, api_client):
        """Test user creation with validation errors."""
        invalid_data = {"name": "", "email": "invalid-email"}
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=400,
                data={"error": "Validation failed", "details": ["Invalid email", "Name required"]},
                headers={},
                response_time=0.1,
                success=False
            )
            
            response = await api_client.post("/users", data=invalid_data)
            assert not response.success
            assert response.status_code == 400

    @pytest.mark.api
    async def test_update_user_success(self, api_client, sample_user_data):
        """Test successful user update."""
        user_id = sample_user_data["id"]
        update_data = {"name": "Updated Name"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={**sample_user_data, **update_data},
                headers={},
                response_time=0.15,
                success=True
            )
            
            response = await api_client.put(f"/users/{user_id}", data=update_data)
            assert response.success
            assert response.data["name"] == "Updated Name"

    @pytest.mark.api
    async def test_delete_user_success(self, api_client, sample_user_data):
        """Test successful user deletion."""
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=204,
                data=None,
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.delete(f"/users/{user_id}")
            assert response.success
            assert response.status_code == 204

    @pytest.mark.api
    async def test_list_users_success(self, api_client, sample_user_data):
        """Test successful user listing."""
        users_list = [sample_user_data for _ in range(3)]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"users": users_list, "total": 3},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.get("/users")
            assert response.success
            assert len(response.data["users"]) == 3

    @pytest.mark.api
    async def test_list_users_with_pagination(self, api_client):
        """Test user listing with pagination."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"users": [], "total": 100, "page": 2, "limit": 10},
                headers={},
                response_time=0.15,
                success=True
            )
            
            params = {"page": 2, "limit": 10}
            response = await api_client.get("/users", params=params)
            assert response.success
            assert response.data["page"] == 2

    @pytest.mark.api
    async def test_search_users_by_email(self, api_client, sample_user_data):
        """Test user search by email."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"users": [sample_user_data], "total": 1},
                headers={},
                response_time=0.1,
                success=True
            )
            
            params = {"email": sample_user_data["email"]}
            response = await api_client.get("/users/search", params=params)
            assert response.success
            assert response.data["total"] == 1

    @pytest.mark.api
    async def test_user_profile_image_upload(self, api_client, sample_user_data):
        """Test user profile image upload."""
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"image_url": f"https://example.com/users/{user_id}/avatar.jpg"},
                headers={},
                response_time=0.5,
                success=True
            )
            
            response = await api_client.post(f"/users/{user_id}/avatar", data={"image": "base64data"})
            assert response.success
            assert "image_url" in response.data

    @pytest.mark.api
    async def test_user_password_change(self, api_client, sample_user_data):
        """Test user password change."""
        user_id = sample_user_data["id"]
        password_data = {"old_password": "old123", "new_password": "new456"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Password updated successfully"},
                headers={},
                response_time=0.3,
                success=True
            )
            
            response = await api_client.post(f"/users/{user_id}/password", data=password_data)
            assert response.success

    @pytest.mark.api
    async def test_user_email_verification(self, api_client, sample_user_data):
        """Test user email verification."""
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"verified": True, "message": "Email verified"},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post(f"/users/{user_id}/verify-email", data={"token": "verify123"})
            assert response.success
            assert response.data["verified"]

    @pytest.mark.api
    async def test_user_preferences_update(self, api_client, sample_user_data):
        """Test user preferences update."""
        user_id = sample_user_data["id"]
        preferences = {"theme": "dark", "notifications": True, "language": "en"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"preferences": preferences},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.put(f"/users/{user_id}/preferences", data=preferences)
            assert response.success

    @pytest.mark.api
    async def test_user_activity_log(self, api_client, sample_user_data):
        """Test user activity log retrieval."""
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"activities": [{"action": "login", "timestamp": "2024-01-01T00:00:00Z"}]},
                headers={},
                response_time=0.15,
                success=True
            )
            
            response = await api_client.get(f"/users/{user_id}/activities")
            assert response.success
            assert len(response.data["activities"]) > 0

    @pytest.mark.api
    async def test_user_deactivation(self, api_client, sample_user_data):
        """Test user account deactivation."""
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Account deactivated", "status": "inactive"},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post(f"/users/{user_id}/deactivate")
            assert response.success

    @pytest.mark.api
    async def test_user_reactivation(self, api_client, sample_user_data):
        """Test user account reactivation."""
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Account reactivated", "status": "active"},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post(f"/users/{user_id}/reactivate")
            assert response.success

    @pytest.mark.api
    async def test_user_role_assignment(self, api_client, sample_user_data):
        """Test user role assignment."""
        user_id = sample_user_data["id"]
        role_data = {"role": "admin", "permissions": ["read", "write", "delete"]}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"user_id": user_id, **role_data},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post(f"/users/{user_id}/roles", data=role_data)
            assert response.success

    @pytest.mark.api
    async def test_user_session_management(self, api_client, sample_user_data):
        """Test user session management."""
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"sessions": [{"id": "sess123", "created_at": "2024-01-01T00:00:00Z", "active": True}]},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get(f"/users/{user_id}/sessions")
            assert response.success

    @pytest.mark.api
    async def test_user_export_data(self, api_client, sample_user_data):
        """Test user data export."""
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"export_url": f"https://example.com/exports/{user_id}.json", "expires_at": "2024-01-02T00:00:00Z"},
                headers={},
                response_time=1.0,
                success=True
            )
            
            response = await api_client.post(f"/users/{user_id}/export")
            assert response.success
            assert "export_url" in response.data


class TestProductAPIEndpoints:
    """Test product-related API endpoints (20 tests)."""
    
    @pytest.mark.api
    async def test_get_product_success(self, api_client, sample_product_data):
        """Test successful product retrieval."""
        product_id = sample_product_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data=sample_product_data,
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get(f"/products/{product_id}")
            assert response.success
            assert response.data["id"] == product_id

    @pytest.mark.api
    async def test_create_product_success(self, api_client, sample_product_data):
        """Test successful product creation."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=201,
                data=sample_product_data,
                headers={"Location": f"/products/{sample_product_data['id']}"},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post("/products", data=sample_product_data)
            assert response.success
            assert response.status_code == 201

    @pytest.mark.api
    async def test_update_product_price(self, api_client, sample_product_data):
        """Test product price update."""
        product_id = sample_product_data["id"]
        new_price = 99.99
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={**sample_product_data, "price": new_price},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.patch(f"/products/{product_id}", data={"price": new_price})
            assert response.success
            assert response.data["price"] == new_price

    @pytest.mark.api
    async def test_delete_product_success(self, api_client, sample_product_data):
        """Test successful product deletion."""
        product_id = sample_product_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=204,
                data=None,
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.delete(f"/products/{product_id}")
            assert response.success
            assert response.status_code == 204

    @pytest.mark.api
    async def test_list_products_by_category(self, api_client, sample_product_data):
        """Test product listing by category."""
        category = sample_product_data["category"]
        products = [sample_product_data for _ in range(5)]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"products": products, "total": 5, "category": category},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.get(f"/products?category={category}")
            assert response.success
            assert len(response.data["products"]) == 5

    @pytest.mark.api
    async def test_search_products_by_name(self, api_client, sample_product_data):
        """Test product search by name."""
        search_term = sample_product_data["name"][:5]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"products": [sample_product_data], "total": 1, "query": search_term},
                headers={},
                response_time=0.15,
                success=True
            )
            
            response = await api_client.get(f"/products/search?q={search_term}")
            assert response.success

    @pytest.mark.api
    async def test_product_inventory_update(self, api_client, sample_product_data):
        """Test product inventory update."""
        product_id = sample_product_data["id"]
        new_stock = 150
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={**sample_product_data, "stock": new_stock},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post(f"/products/{product_id}/inventory", data={"stock": new_stock})
            assert response.success

    @pytest.mark.api
    async def test_product_reviews_list(self, api_client, sample_product_data):
        """Test product reviews listing."""
        product_id = sample_product_data["id"]
        reviews = [{"rating": 5, "comment": "Great product!", "user_id": "user123"}]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"reviews": reviews, "average_rating": 5.0, "total_reviews": 1},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get(f"/products/{product_id}/reviews")
            assert response.success

    @pytest.mark.api
    async def test_product_image_upload(self, api_client, sample_product_data):
        """Test product image upload."""
        product_id = sample_product_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"image_urls": [f"https://example.com/products/{product_id}/image1.jpg"]},
                headers={},
                response_time=0.5,
                success=True
            )
            
            response = await api_client.post(f"/products/{product_id}/images", data={"images": ["base64image"]})
            assert response.success

    @pytest.mark.api
    async def test_product_recommendations(self, api_client, sample_product_data):
        """Test product recommendations."""
        product_id = sample_product_data["id"]
        recommendations = [sample_product_data for _ in range(3)]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"recommendations": recommendations, "algorithm": "collaborative_filtering"},
                headers={},
                response_time=0.3,
                success=True
            )
            
            response = await api_client.get(f"/products/{product_id}/recommendations")
            assert response.success

    @pytest.mark.api
    async def test_product_price_history(self, api_client, sample_product_data):
        """Test product price history."""
        product_id = sample_product_data["id"]
        history = [{"price": 100.0, "date": "2024-01-01"}, {"price": 95.0, "date": "2024-01-15"}]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"price_history": history, "current_price": 95.0},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get(f"/products/{product_id}/price-history")
            assert response.success

    @pytest.mark.api
    async def test_product_availability_check(self, api_client, sample_product_data):
        """Test product availability check."""
        product_id = sample_product_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"available": True, "stock": 50, "delivery_estimate": "2-3 days"},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get(f"/products/{product_id}/availability")
            assert response.success

    @pytest.mark.api
    async def test_bulk_product_update(self, api_client):
        """Test bulk product update."""
        updates = [{"id": "prod1", "price": 100}, {"id": "prod2", "stock": 50}]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"updated": 2, "failed": 0, "results": updates},
                headers={},
                response_time=0.5,
                success=True
            )
            
            response = await api_client.post("/products/bulk-update", data={"updates": updates})
            assert response.success

    @pytest.mark.api
    async def test_product_variant_management(self, api_client, sample_product_data):
        """Test product variant management."""
        product_id = sample_product_data["id"]
        variant = {"size": "L", "color": "red", "price": 105.0, "stock": 20}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=201,
                data={"variant_id": "var123", **variant},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post(f"/products/{product_id}/variants", data=variant)
            assert response.success

    @pytest.mark.api
    async def test_product_category_tree(self, api_client):
        """Test product category tree."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"categories": [{"id": "cat1", "name": "Electronics", "children": [{"id": "cat2", "name": "Phones"}]}]},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get("/products/categories")
            assert response.success

    @pytest.mark.api
    async def test_product_wishlist_add(self, api_client, sample_product_data, sample_user_data):
        """Test adding product to wishlist."""
        product_id = sample_product_data["id"]
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Added to wishlist", "wishlist_count": 5},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post(f"/users/{user_id}/wishlist", data={"product_id": product_id})
            assert response.success

    @pytest.mark.api
    async def test_product_comparison(self, api_client, sample_product_data):
        """Test product comparison."""
        product_ids = [sample_product_data["id"], "prod2", "prod3"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"products": [sample_product_data], "comparison_matrix": {}},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post("/products/compare", data={"product_ids": product_ids})
            assert response.success

    @pytest.mark.api
    async def test_product_rating_analytics(self, api_client, sample_product_data):
        """Test product rating analytics."""
        product_id = sample_product_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"average_rating": 4.5, "rating_distribution": {"5": 50, "4": 30, "3": 15, "2": 3, "1": 2}},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get(f"/products/{product_id}/analytics/ratings")
            assert response.success

    @pytest.mark.api
    async def test_product_view_tracking(self, api_client, sample_product_data, sample_user_data):
        """Test product view tracking."""
        product_id = sample_product_data["id"]
        user_id = sample_user_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"view_recorded": True, "total_views": 1250},
                headers={},
                response_time=0.05,
                success=True
            )
            
            response = await api_client.post(f"/products/{product_id}/views", data={"user_id": user_id})
            assert response.success


class TestOrderAPIEndpoints:
    """Test order-related API endpoints (20 tests)."""
    
    @pytest.mark.api
    async def test_create_order_success(self, api_client, sample_order_data):
        """Test successful order creation."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=201,
                data=sample_order_data,
                headers={"Location": f"/orders/{sample_order_data['id']}"},
                response_time=0.3,
                success=True
            )
            
            response = await api_client.post("/orders", data=sample_order_data)
            assert response.success
            assert response.status_code == 201

    @pytest.mark.api
    async def test_get_order_success(self, api_client, sample_order_data):
        """Test successful order retrieval."""
        order_id = sample_order_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data=sample_order_data,
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get(f"/orders/{order_id}")
            assert response.success
            assert response.data["id"] == order_id

    @pytest.mark.api
    async def test_update_order_status(self, api_client, sample_order_data):
        """Test order status update."""
        order_id = sample_order_data["id"]
        new_status = "shipped"
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={**sample_order_data, "status": new_status},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.patch(f"/orders/{order_id}", data={"status": new_status})
            assert response.success
            assert response.data["status"] == new_status

    @pytest.mark.api
    async def test_cancel_order_success(self, api_client, sample_order_data):
        """Test successful order cancellation."""
        order_id = sample_order_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={**sample_order_data, "status": "cancelled", "cancelled_at": "2024-01-01T12:00:00Z"},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post(f"/orders/{order_id}/cancel")
            assert response.success

    @pytest.mark.api
    async def test_list_user_orders(self, api_client, sample_user_data, sample_order_data):
        """Test listing user orders."""
        user_id = sample_user_data["id"]
        orders = [sample_order_data for _ in range(3)]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"orders": orders, "total": 3, "user_id": user_id},
                headers={},
                response_time=0.15,
                success=True
            )
            
            response = await api_client.get(f"/users/{user_id}/orders")
            assert response.success
            assert len(response.data["orders"]) == 3

    @pytest.mark.api
    async def test_order_payment_processing(self, api_client, sample_order_data):
        """Test order payment processing."""
        order_id = sample_order_data["id"]
        payment_data = {"method": "credit_card", "card_token": "tok_123"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"payment_status": "completed", "transaction_id": "txn_456"},
                headers={},
                response_time=1.2,
                success=True
            )
            
            response = await api_client.post(f"/orders/{order_id}/payment", data=payment_data)
            assert response.success

    @pytest.mark.api
    async def test_order_shipping_tracking(self, api_client, sample_order_data):
        """Test order shipping tracking."""
        order_id = sample_order_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"tracking_number": "TRK123456", "carrier": "UPS", "status": "in_transit"},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.get(f"/orders/{order_id}/tracking")
            assert response.success

    @pytest.mark.api
    async def test_order_refund_request(self, api_client, sample_order_data):
        """Test order refund request."""
        order_id = sample_order_data["id"]
        refund_data = {"reason": "defective_product", "amount": 50.0}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"refund_id": "ref_789", "status": "pending", "amount": 50.0},
                headers={},
                response_time=0.3,
                success=True
            )
            
            response = await api_client.post(f"/orders/{order_id}/refund", data=refund_data)
            assert response.success

    @pytest.mark.api
    async def test_order_invoice_generation(self, api_client, sample_order_data):
        """Test order invoice generation."""
        order_id = sample_order_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"invoice_url": f"https://example.com/invoices/{order_id}.pdf", "invoice_number": "INV-001"},
                headers={},
                response_time=0.5,
                success=True
            )
            
            response = await api_client.post(f"/orders/{order_id}/invoice")
            assert response.success

    @pytest.mark.api
    async def test_order_delivery_confirmation(self, api_client, sample_order_data):
        """Test order delivery confirmation."""
        order_id = sample_order_data["id"]
        confirmation_data = {"delivered_at": "2024-01-10T15:30:00Z", "signature": "delivered"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={**sample_order_data, "status": "delivered", **confirmation_data},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post(f"/orders/{order_id}/delivery-confirm", data=confirmation_data)
            assert response.success

    @pytest.mark.api
    async def test_order_items_modification(self, api_client, sample_order_data):
        """Test order items modification."""
        order_id = sample_order_data["id"]
        modifications = {"add_items": [{"product_id": "prod123", "quantity": 1}], "remove_items": []}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Order modified", "new_total": 150.0},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post(f"/orders/{order_id}/modify", data=modifications)
            assert response.success

    @pytest.mark.api
    async def test_order_notes_management(self, api_client, sample_order_data):
        """Test order notes management."""
        order_id = sample_order_data["id"]
        note_data = {"note": "Customer requested gift wrapping", "internal": False}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"note_id": "note123", **note_data, "created_at": "2024-01-01T12:00:00Z"},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post(f"/orders/{order_id}/notes", data=note_data)
            assert response.success

    @pytest.mark.api
    async def test_order_priority_update(self, api_client, sample_order_data):
        """Test order priority update."""
        order_id = sample_order_data["id"]
        priority_data = {"priority": "high", "reason": "VIP customer"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={**sample_order_data, **priority_data},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.patch(f"/orders/{order_id}/priority", data=priority_data)
            assert response.success

    @pytest.mark.api
    async def test_order_analytics_summary(self, api_client):
        """Test order analytics summary."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"total_orders": 1500, "total_revenue": 75000.0, "average_order_value": 50.0},
                headers={},
                response_time=0.3,
                success=True
            )
            
            response = await api_client.get("/orders/analytics/summary")
            assert response.success

    @pytest.mark.api
    async def test_order_bulk_status_update(self, api_client):
        """Test bulk order status update."""
        bulk_data = {"order_ids": ["order1", "order2", "order3"], "status": "shipped"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"updated": 3, "failed": 0, "results": []},
                headers={},
                response_time=0.5,
                success=True
            )
            
            response = await api_client.post("/orders/bulk-update-status", data=bulk_data)
            assert response.success

    @pytest.mark.api
    async def test_order_recommendation_engine(self, api_client, sample_order_data):
        """Test order recommendation engine."""
        order_id = sample_order_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"recommendations": [{"product_id": "prod456", "score": 0.85}], "algorithm": "collaborative_filtering"},
                headers={},
                response_time=0.4,
                success=True
            )
            
            response = await api_client.get(f"/orders/{order_id}/recommendations")
            assert response.success

    @pytest.mark.api
    async def test_order_return_initiation(self, api_client, sample_order_data):
        """Test order return initiation."""
        order_id = sample_order_data["id"]
        return_data = {"items": [{"product_id": "prod123", "quantity": 1, "reason": "damaged"}]}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"return_id": "ret_789", "status": "approved", "return_label_url": "https://example.com/label.pdf"},
                headers={},
                response_time=0.3,
                success=True
            )
            
            response = await api_client.post(f"/orders/{order_id}/return", data=return_data)
            assert response.success

    @pytest.mark.api
    async def test_order_loyalty_points_calculation(self, api_client, sample_order_data):
        """Test order loyalty points calculation."""
        order_id = sample_order_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"points_earned": 100, "points_redeemed": 0, "total_points": 1250},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.get(f"/orders/{order_id}/loyalty-points")
            assert response.success

    @pytest.mark.api
    async def test_order_fraud_detection(self, api_client, sample_order_data):
        """Test order fraud detection."""
        order_id = sample_order_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"fraud_score": 0.15, "risk_level": "low", "flags": []},
                headers={},
                response_time=0.8,
                success=True
            )
            
            response = await api_client.get(f"/orders/{order_id}/fraud-check")
            assert response.success

    @pytest.mark.api
    async def test_order_inventory_reservation(self, api_client, sample_order_data):
        """Test order inventory reservation."""
        order_id = sample_order_data["id"]
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"reserved": True, "reservation_id": "res_456", "expires_at": "2024-01-01T13:00:00Z"},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post(f"/orders/{order_id}/reserve-inventory")
            assert response.success


class TestAuthenticationAPIEndpoints:
    """Test authentication-related API endpoints (20 tests)."""
    
    @pytest.mark.api
    async def test_login_success(self, api_client):
        """Test successful user login."""
        login_data = {"email": "user@example.com", "password": "password123"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"access_token": "jwt_token", "refresh_token": "refresh_token", "expires_in": 3600},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post("/auth/login", data=login_data)
            assert response.success
            assert "access_token" in response.data

    @pytest.mark.api
    async def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials."""
        login_data = {"email": "user@example.com", "password": "wrongpassword"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=401,
                data={"error": "Invalid credentials"},
                headers={},
                response_time=0.1,
                success=False
            )
            
            response = await api_client.post("/auth/login", data=login_data)
            assert not response.success
            assert response.status_code == 401

    @pytest.mark.api
    async def test_register_success(self, api_client, sample_user_data):
        """Test successful user registration."""
        register_data = {**sample_user_data, "password": "newpassword123"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=201,
                data={"user_id": sample_user_data["id"], "message": "Registration successful"},
                headers={},
                response_time=0.3,
                success=True
            )
            
            response = await api_client.post("/auth/register", data=register_data)
            assert response.success
            assert response.status_code == 201

    @pytest.mark.api
    async def test_token_refresh_success(self, api_client):
        """Test successful token refresh."""
        refresh_data = {"refresh_token": "valid_refresh_token"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"access_token": "new_jwt_token", "expires_in": 3600},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post("/auth/refresh", data=refresh_data)
            assert response.success

    @pytest.mark.api
    async def test_logout_success(self, api_client):
        """Test successful logout."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Logout successful"},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post("/auth/logout")
            assert response.success

    @pytest.mark.api
    async def test_password_reset_request(self, api_client):
        """Test password reset request."""
        reset_data = {"email": "user@example.com"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Password reset email sent", "reset_token_sent": True},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post("/auth/password-reset", data=reset_data)
            assert response.success

    @pytest.mark.api
    async def test_password_reset_confirm(self, api_client):
        """Test password reset confirmation."""
        confirm_data = {"token": "reset_token", "new_password": "newpassword456"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Password reset successful", "password_updated": True},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post("/auth/password-reset-confirm", data=confirm_data)
            assert response.success

    @pytest.mark.api
    async def test_email_verification_send(self, api_client):
        """Test email verification send."""
        email_data = {"email": "user@example.com"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Verification email sent", "verification_sent": True},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post("/auth/verify-email", data=email_data)
            assert response.success

    @pytest.mark.api
    async def test_email_verification_confirm(self, api_client):
        """Test email verification confirmation."""
        verify_data = {"token": "verification_token"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Email verified successfully", "email_verified": True},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post("/auth/verify-email-confirm", data=verify_data)
            assert response.success

    @pytest.mark.api
    async def test_two_factor_auth_enable(self, api_client):
        """Test two-factor authentication enable."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"qr_code": "data:image/png;base64,iVBOR...", "secret": "SECRET123", "backup_codes": ["123456"]},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post("/auth/2fa/enable")
            assert response.success

    @pytest.mark.api
    async def test_two_factor_auth_verify(self, api_client):
        """Test two-factor authentication verification."""
        verify_data = {"code": "123456"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"verified": True, "access_token": "jwt_token_with_2fa"},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post("/auth/2fa/verify", data=verify_data)
            assert response.success

    @pytest.mark.api
    async def test_oauth_google_login(self, api_client):
        """Test OAuth Google login."""
        oauth_data = {"code": "google_oauth_code", "state": "random_state"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"access_token": "jwt_token", "user_id": "user123", "provider": "google"},
                headers={},
                response_time=0.5,
                success=True
            )
            
            response = await api_client.post("/auth/oauth/google", data=oauth_data)
            assert response.success

    @pytest.mark.api
    async def test_oauth_github_login(self, api_client):
        """Test OAuth GitHub login."""
        oauth_data = {"code": "github_oauth_code", "state": "random_state"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"access_token": "jwt_token", "user_id": "user123", "provider": "github"},
                headers={},
                response_time=0.5,
                success=True
            )
            
            response = await api_client.post("/auth/oauth/github", data=oauth_data)
            assert response.success

    @pytest.mark.api
    async def test_session_validation(self, api_client):
        """Test session validation."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"valid": True, "user_id": "user123", "expires_at": "2024-01-01T23:59:59Z"},
                headers={},
                response_time=0.05,
                success=True
            )
            
            response = await api_client.get("/auth/validate")
            assert response.success

    @pytest.mark.api
    async def test_change_password_authenticated(self, api_client):
        """Test authenticated password change."""
        password_data = {"current_password": "oldpass123", "new_password": "newpass456"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"message": "Password changed successfully", "password_changed": True},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.post("/auth/change-password", data=password_data)
            assert response.success

    @pytest.mark.api
    async def test_account_lockout_status(self, api_client):
        """Test account lockout status check."""
        email_data = {"email": "user@example.com"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"locked": False, "failed_attempts": 2, "lockout_expires": None},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post("/auth/lockout-status", data=email_data)
            assert response.success

    @pytest.mark.api
    async def test_api_key_generation(self, api_client):
        """Test API key generation."""
        key_data = {"name": "My API Key", "permissions": ["read", "write"]}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=201,
                data={"api_key": "ak_1234567890abcdef", "name": "My API Key", "created_at": "2024-01-01T12:00:00Z"},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post("/auth/api-keys", data=key_data)
            assert response.success

    @pytest.mark.api
    async def test_device_registration(self, api_client):
        """Test device registration for push notifications."""
        device_data = {"device_token": "device123", "platform": "ios", "app_version": "1.0.0"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"device_id": "dev456", "registered": True},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post("/auth/devices", data=device_data)
            assert response.success

    @pytest.mark.api
    async def test_security_audit_log(self, api_client):
        """Test security audit log retrieval."""
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"events": [{"event": "login", "ip": "192.168.1.1", "timestamp": "2024-01-01T12:00:00Z"}], "total": 10},
                headers={},
                response_time=0.2,
                success=True
            )
            
            response = await api_client.get("/auth/audit-log")
            assert response.success

    @pytest.mark.api
    async def test_token_revocation(self, api_client):
        """Test token revocation."""
        revoke_data = {"token": "jwt_token_to_revoke"}
        
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = APIResponse(
                status_code=200,
                data={"revoked": True, "message": "Token revoked successfully"},
                headers={},
                response_time=0.1,
                success=True
            )
            
            response = await api_client.post("/auth/revoke", data=revoke_data)
            assert response.success 