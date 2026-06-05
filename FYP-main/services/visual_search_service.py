import io
import base64
import logging
import requests
from PIL import Image
from decouple import config

logger = logging.getLogger(__name__)

GROQ_API_KEY = config('LLAMA_API_KEY', default='')
GROQ_ENDPOINT = 'https://api.groq.com/openai/v1/chat/completions'


def _describe_image(image: Image.Image) -> str:
    """
    Send image to Groq vision model and get a product search description back.
    """
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    b64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    prompt = (
        "Look at this product image and describe it in a short search query of 5-10 words. "
        "Focus on: type of item, color, style, pattern, material if visible. "
        "Examples: 'red bridal lehenga golden embroidery', 'blue denim jacket casual', "
        "'gold necklace floral design', 'gaming laptop black rgb'. "
        "Return ONLY the short search query, nothing else, no punctuation."
    )

    payload = {
        'model': 'meta-llama/llama-4-scout-17b-16e-instruct',
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{b64_image}'
                        }
                    },
                    {
                        'type': 'text',
                        'text': prompt
                    }
                ]
            }
        ],
        'temperature': 0.3,
        'max_tokens': 50,
    }

    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json',
    }

    response = requests.post(GROQ_ENDPOINT, json=payload, headers=headers, timeout=20)
    response.raise_for_status()

    description = response.json()['choices'][0]['message']['content'].strip().lower()
    logger.info('Groq vision description: %s', description)
    return description


def find_similar_products(uploaded_image: Image.Image, top_k: int = 6):
    from products.models import Product

    # Broad stop words — generic terms that match everything and mean nothing
    STOP_WORDS = {
        'the', 'and', 'for', 'with', 'this', 'that', 'from',
        'are', 'was', 'has', 'have', 'its', 'into', 'onto',
        'very', 'also', 'some', 'such', 'than', 'then',
        # Generic product words that cause false positives
        'product', 'item', 'good', 'nice', 'quality', 'design',
        'style', 'color', 'image', 'photo', 'picture', 'looking',
        'high', 'new', 'best', 'top', 'great', 'big', 'small',
    }

    description = _describe_image(uploaded_image)
    logger.info('Groq description: %s', description)

    # Clean and filter keywords
    raw_words = description.replace(',', ' ').replace('-', ' ').split()
    keywords = [
        word.strip().lower()
        for word in raw_words
        if len(word.strip()) > 2 and word.strip().lower() not in STOP_WORDS
    ]

    logger.info('Filtered keywords: %s', keywords)

    if not keywords:
        return [], description

    # Score each product by how many keywords match
    all_products = (
        Product.objects
        .filter(is_available=True)
        .select_related('category')
    )

    scored = []
    for product in all_products:
        # Build searchable text blob from all product fields
        searchable = ' '.join([
            product.name or '',
            product.description or '',
            product.brand or '',
            product.category.name if product.category else '',
        ]).lower()

        # Count keyword hits
        score = sum(1 for kw in keywords if kw in searchable)

        # Must match at least 40% of keywords AND minimum 2 absolute hits
        min_required = max(2, int(len(keywords) * 0.4))
        if score >= min_required:
            scored.append((product, score))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    matched_products = [p for p, score in scored[:top_k]]
    return matched_products, description
    """
    Use Groq vision to describe the uploaded image then search
    the product catalog using that description.
    Returns a tuple of (matched_products, search_description)
    """
    from products.models import Product
    from django.db.models import Q

    description = _describe_image(uploaded_image)

    keywords = [word.strip() for word in description.split() if len(word.strip()) > 2]

    if not keywords:
        return [], description

    query = Q()
    for keyword in keywords:
        query |= Q(name__icontains=keyword)
        query |= Q(description__icontains=keyword)
        query |= Q(brand__icontains=keyword)
        query |= Q(category__name__icontains=keyword)

    products = (
        Product.objects
        .filter(is_available=True)
        .filter(query)
        .select_related('category')
        .distinct()[:top_k]
    )

    return list(products), description