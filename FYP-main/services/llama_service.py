import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import requests
from requests.exceptions import RequestException
from decouple import config


logger = logging.getLogger(__name__)


def _build_prompt(*, product_price: Decimal, min_price: Decimal, offer: Decimal) -> str:
    product_price = Decimal(str(product_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    min_price = Decimal(str(min_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    offer = Decimal(str(offer)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return (
        "You are an e-commerce price negotiation assistant.\n\n"
        f"Listed product price: {product_price}\n"
        f"Minimum allowed price: {min_price}\n"
        "Maximum discount allowed: 20%\n"
        f"Customer offer: {offer}\n\n"
        "You must respond in EXACTLY one of these formats:\n\n"
        "ACCEPT\n"
        "REJECT\n"
        "COUNTER: <numeric price>\n\n"
        "Rules:\n"
        "- Never go below minimum allowed price.\n"
        "- Counter price must be between minimum price and listed price.\n"
        "- Do not explain.\n"
        "- Do not add extra text.\n"
        "- Do not include currency symbols.\n"
    )


def _parse_response(*, raw_text: str, min_price: Decimal, product_price: Decimal, offer: Decimal):
    text = (raw_text or '').strip()

    if text == 'ACCEPT':
        return {'decision': 'accept', 'counter_price': None}

    if text == 'REJECT':
        return {'decision': 'reject', 'counter_price': None}

    if text.startswith('COUNTER:'):
        candidate = text[len('COUNTER:'):].strip()
        try:
            price = Decimal(candidate)
        except (InvalidOperation, TypeError):
            price = None

        if price is not None:
            price = Decimal(str(price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if price < min_price:
                price = min_price
            if price > product_price:
                price = product_price
            return {'decision': 'counter', 'counter_price': price}

    fallback = ((offer + product_price) / 2).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if fallback < min_price:
        fallback = min_price
    if fallback > product_price:
        fallback = product_price

    return {'decision': 'counter', 'counter_price': fallback}


def negotiate_price(*, product_price: Decimal, min_price: Decimal, offer: Decimal):
    endpoint = config('LLAMA_ENDPOINT', default='')
    api_key = config('LLAMA_API_KEY', default='')

    raw_output = ''

    product_price = Decimal(str(product_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    min_price = Decimal(str(min_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    offer = Decimal(str(offer)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    prompt = _build_prompt(product_price=product_price, min_price=min_price, offer=offer)

    if not endpoint or not api_key:
        logger.warning('LLAMA_ENDPOINT or LLAMA_API_KEY not set. Using fallback.')
        parsed = _parse_response(raw_text='', min_price=min_price, product_price=product_price, offer=offer)
        parsed['raw_output'] = raw_output
        return parsed

    payload = {
        'model': 'llama-3.3-70b-versatile',
        'messages': [
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.4,
        'max_tokens': 80,
    }

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        content = ''
        if isinstance(data, dict):
            if isinstance(data.get('choices'), list) and data['choices']:
                choice0 = data['choices'][0] or {}
                message = choice0.get('message') or {}
                content = message.get('content') or ''
            if not content and isinstance(data.get('output_text'), str):
                content = data.get('output_text')

        raw_output = (content or '').strip()
        logger.info('LLAMA negotiation raw output: %s', raw_output)

    except RequestException as e:
        logger.exception('LLAMA negotiation request failed: %s', e)
        raw_output = ''
    except ValueError as e:
        logger.exception('LLAMA negotiation invalid JSON: %s', e)
        raw_output = ''
    except Exception as e:
        logger.exception('LLAMA negotiation unexpected error: %s', e)
        raw_output = ''

    parsed = _parse_response(raw_text=raw_output, min_price=min_price, product_price=product_price, offer=offer)
    parsed['raw_output'] = raw_output
    return parsed


    