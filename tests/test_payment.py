# tests/test_payment.py

def test_create_ai_subscription_order_no_plan_id(client, auth_headers):
    """
    Tests if the student AI subscription endpoint returns a 500 error when no plan ID is configured.
    """
    response = client.post('/api/payment/create-ai-subscription-order', headers=auth_headers, json={})
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['message'] == "Subscription service is not configured for your region. Please contact support."

def test_create_org_ai_subscription_no_plan_id(client, admin_auth_headers):
    """
    Tests if the organization AI subscription endpoint returns a 500 error when no plan ID is configured.
    """
    # This endpoint requires organization context, which is handled by the admin_role_required decorator.
    # The decorator should extract org from the admin user.
    response = client.post('/api/payment/organization/create-ai-subscription', headers=admin_auth_headers)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['message'] == "AI Assistant subscription service is not configured for your region. Please contact support."
