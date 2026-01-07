# app/utils/localization.py

from flask import request
import logging

# A simple logger for localization debugging
log = logging.getLogger(__name__)

def get_country_code():
    """
    Determines the user's country code.
    
    Tries to get the country code from common request headers set by proxies
    or hosting platforms (like Cloudflare or Google App Engine).
    
    Falls back to 'IN' (India) if no specific header is found.
    """
    # Header used by Cloudflare
    cf_country = request.headers.get('CF-IPCountry')
    if cf_country:
        log.debug(f"Detected country '{cf_country}' from 'CF-IPCountry' header.")
        return cf_country.upper()

    # Header used by Google App Engine
    gae_country = request.headers.get('X-Appengine-Country')
    if gae_country:
        log.debug(f"Detected country '{gae_country}' from 'X-Appengine-Country' header.")
        return gae_country.upper()

    # Fallback if no specific header is found
    log.debug("No country-specific header found. Falling back to default 'IN'.")
    return 'IN'

def format_price(price, country_code):
    """
    Formats a price based on the country code.
    
    - For 'IN' (India), it uses the Rupee symbol (₹).
    - For all other countries, it uses the Dollar symbol ($).
    
    Args:
        price (float or int): The numerical price value.
        country_code (str): A two-letter country code (e.g., 'IN', 'US').
        
    Returns:
        str: A formatted price string (e.g., "₹1,250", "$15.00").
    """
    if price is None:
        return "" # Or perhaps "N/A" depending on desired output for None

    try:
        price = float(price)
    except (ValueError, TypeError):
        return str(price) # Return as-is if conversion fails

    if country_code == 'IN':
        # Format for Indian Rupees, with commas for thousands separator.
        return f"₹{price:,.2f}"
    else:
        # Format for US Dollars (or as a general international currency).
        # We'll assume the price is already converted to USD if country is not IN.
        return f"${price:,.2f}"
