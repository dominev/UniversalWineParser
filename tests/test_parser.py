def test_price_extraction():
    response = mock_response(html_with_price)
    price_info = extract_price_and_currency(response)
    assert price_info['price'] == 29.99
    assert price_info['currency'] == 'USD'