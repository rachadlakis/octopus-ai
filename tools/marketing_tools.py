"""
Marketing Agent Tools - Content creation, SEO, and marketing tasks.
"""
import re
import urllib.request
from urllib.parse import quote_plus
from datetime import datetime, timedelta


def analyze_readability(text: str) -> dict:
    """
    Analyze text readability using multiple metrics.

    Args:
        text: Text to analyze

    Returns:
        dict: Readability scores and recommendations
    """
    # Count sentences, words, syllables
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = text.split()

    def count_syllables(word):
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        if word.endswith('e'):
            count -= 1
        return max(1, count)

    total_syllables = sum(count_syllables(w) for w in words)
    total_words = len(words)
    total_sentences = len(sentences)

    if total_words == 0 or total_sentences == 0:
        return {"error": "Text too short to analyze"}

    # Flesch Reading Ease (0-100, higher = easier)
    flesch_ease = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    flesch_ease = max(0, min(100, flesch_ease))

    # Flesch-Kincaid Grade Level
    fk_grade = 0.39 * (total_words / total_sentences) + 11.8 * (total_syllables / total_words) - 15.59
    fk_grade = max(0, fk_grade)

    # Determine reading level
    if flesch_ease >= 80:
        level = "Very Easy (5th grade)"
        audience = "General public, casual readers"
    elif flesch_ease >= 60:
        level = "Standard (8th-9th grade)"
        audience = "Most adults, mainstream content"
    elif flesch_ease >= 40:
        level = "Difficult (College level)"
        audience = "Educated readers, professional content"
    else:
        level = "Very Difficult (Graduate level)"
        audience = "Specialists, academic content"

    # Recommendations
    recommendations = []
    avg_sentence_length = total_words / total_sentences

    if avg_sentence_length > 20:
        recommendations.append("Consider shorter sentences (aim for 15-20 words average)")
    if total_syllables / total_words > 1.5:
        recommendations.append("Use simpler words where possible")
    if flesch_ease < 50:
        recommendations.append("Break up complex ideas into multiple sentences")

    return {
        "flesch_reading_ease": round(flesch_ease, 1),
        "flesch_kincaid_grade": round(fk_grade, 1),
        "reading_level": level,
        "target_audience": audience,
        "stats": {
            "words": total_words,
            "sentences": total_sentences,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_syllables_per_word": round(total_syllables / total_words, 2)
        },
        "recommendations": recommendations
    }


def generate_hashtags(topic: str, count: int = 10) -> dict:
    """
    Generate relevant hashtags for social media content.

    Args:
        topic: The topic or content theme
        count: Number of hashtags to generate

    Returns:
        dict: Contains 'hashtags' list
    """
    # Common hashtag patterns and modifiers
    modifiers = [
        "", "tips", "101", "hacks", "life", "daily", "inspo",
        "community", "lovers", "world", "gram", "oftheday"
    ]

    # Clean and process topic
    words = re.sub(r'[^\w\s]', '', topic.lower()).split()

    hashtags = set()

    # Single word hashtags
    for word in words[:3]:
        if len(word) > 2:
            hashtags.add(f"#{word}")
            for mod in modifiers[:5]:
                if mod:
                    hashtags.add(f"#{word}{mod}")

    # Combined words
    if len(words) >= 2:
        combined = ''.join(words[:2])
        hashtags.add(f"#{combined}")
        combined = ''.join(words[:3]) if len(words) >= 3 else combined
        hashtags.add(f"#{combined}")

    # Common marketing hashtags
    marketing_tags = [
        "#marketing", "#digitalmarketing", "#contentcreator",
        "#socialmedia", "#branding", "#business", "#entrepreneur",
        "#growthhacking", "#startup", "#success"
    ]

    # Add some generic popular tags based on topic type
    if any(w in topic.lower() for w in ['tech', 'software', 'code', 'ai']):
        hashtags.update(['#tech', '#technology', '#innovation', '#ai', '#coding'])
    if any(w in topic.lower() for w in ['food', 'cook', 'recipe']):
        hashtags.update(['#foodie', '#foodporn', '#yummy', '#homemade', '#delicious'])
    if any(w in topic.lower() for w in ['travel', 'trip', 'vacation']):
        hashtags.update(['#travel', '#wanderlust', '#adventure', '#explore', '#vacation'])
    if any(w in topic.lower() for w in ['fitness', 'health', 'workout']):
        hashtags.update(['#fitness', '#health', '#workout', '#gym', '#motivation'])

    # Return limited list
    result = sorted(list(hashtags))[:count]

    return {
        "topic": topic,
        "hashtags": result,
        "count": len(result),
        "tip": "Mix popular and niche hashtags for best reach"
    }


def create_social_post(content: str, platform: str, include_hashtags: bool = True) -> dict:
    """
    Format content for specific social media platforms.

    Args:
        content: The main content/message
        platform: Target platform (twitter, linkedin, instagram, facebook)
        include_hashtags: Whether to add relevant hashtags

    Returns:
        dict: Formatted post with platform-specific adjustments
    """
    platform = platform.lower()

    limits = {
        "twitter": 280,
        "linkedin": 3000,
        "instagram": 2200,
        "facebook": 63206,
        "threads": 500
    }

    char_limit = limits.get(platform, 1000)

    # Platform-specific formatting
    if platform == "twitter":
        # Concise, punchy
        formatted = content[:250] if len(content) > 250 else content
        tips = ["Use threads for longer content", "Include 1-2 relevant hashtags", "Add a call-to-action"]

    elif platform == "linkedin":
        # Professional, can use line breaks for readability
        lines = content.split('. ')
        formatted = '.\n\n'.join(lines)
        tips = ["Start with a hook in first line", "Use emojis sparingly", "End with a question to drive engagement"]

    elif platform == "instagram":
        # Can be longer, emoji-friendly
        formatted = content
        tips = ["First line is most important (preview)", "Use line breaks for readability", "Put hashtags in first comment or end of caption"]

    elif platform == "facebook":
        formatted = content
        tips = ["Shorter posts often perform better", "Questions drive comments", "Native video gets more reach"]

    else:
        formatted = content
        tips = []

    # Check length
    is_over_limit = len(formatted) > char_limit
    if is_over_limit:
        formatted = formatted[:char_limit-3] + "..."

    # Generate hashtags if requested
    hashtags = []
    if include_hashtags:
        # Extract main topic words
        words = re.findall(r'\b\w{4,}\b', content.lower())[:3]
        hashtags = [f"#{w}" for w in words]

    return {
        "platform": platform,
        "formatted_content": formatted,
        "character_count": len(formatted),
        "character_limit": char_limit,
        "is_within_limit": not is_over_limit,
        "suggested_hashtags": hashtags,
        "tips": tips
    }


def analyze_headline(headline: str) -> dict:
    """
    Analyze headline effectiveness for clicks and engagement.

    Args:
        headline: The headline to analyze

    Returns:
        dict: Analysis with scores and suggestions
    """
    score = 50  # Base score
    feedback = []

    words = headline.split()
    word_count = len(words)

    # Length analysis (optimal: 6-12 words)
    if 6 <= word_count <= 12:
        score += 10
        feedback.append("✓ Good length (6-12 words)")
    elif word_count < 6:
        score -= 5
        feedback.append("✗ Too short - add more context")
    else:
        score -= 5
        feedback.append("✗ Too long - try to be more concise")

    # Power words
    power_words = [
        'ultimate', 'essential', 'proven', 'secret', 'amazing',
        'free', 'new', 'how', 'why', 'best', 'top', 'guide',
        'easy', 'simple', 'quick', 'instant', 'powerful',
        'exclusive', 'limited', 'guaranteed', 'discover'
    ]

    headline_lower = headline.lower()
    found_power_words = [w for w in power_words if w in headline_lower]
    if found_power_words:
        score += len(found_power_words) * 5
        feedback.append(f"✓ Contains power words: {', '.join(found_power_words)}")
    else:
        feedback.append("✗ Add power words to increase impact")

    # Numbers
    if re.search(r'\d+', headline):
        score += 10
        feedback.append("✓ Contains numbers (increases clicks)")

    # Question
    if '?' in headline:
        score += 5
        feedback.append("✓ Question format engages curiosity")

    # Emotional words
    emotional_words = [
        'love', 'hate', 'fear', 'surprise', 'angry', 'happy',
        'shocking', 'inspiring', 'heartbreaking', 'hilarious'
    ]
    found_emotional = [w for w in emotional_words if w in headline_lower]
    if found_emotional:
        score += 5
        feedback.append(f"✓ Emotional trigger: {', '.join(found_emotional)}")

    # Clarity check
    if ':' in headline or '-' in headline:
        score += 5
        feedback.append("✓ Good use of separators for clarity")

    # Cap score at 100
    score = min(100, max(0, score))

    # Rating
    if score >= 80:
        rating = "Excellent"
    elif score >= 60:
        rating = "Good"
    elif score >= 40:
        rating = "Average"
    else:
        rating = "Needs Work"

    return {
        "headline": headline,
        "score": score,
        "rating": rating,
        "word_count": word_count,
        "feedback": feedback,
        "suggestions": [
            "Try starting with a number (e.g., '7 Ways to...')",
            "Use 'How to' or 'Why' for educational content",
            "Add urgency with words like 'Now', 'Today', 'Must'"
        ] if score < 70 else []
    }


def create_content_calendar(topics: list, start_date: str = None, posts_per_week: int = 3) -> dict:
    """
    Generate a content calendar for planned topics.

    Args:
        topics: List of content topics
        start_date: Start date (YYYY-MM-DD), defaults to today
        posts_per_week: Number of posts per week

    Returns:
        dict: Content calendar with scheduled dates
    """
    if start_date:
        try:
            current_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}
    else:
        current_date = datetime.now()

    # Best posting days (typically Tue, Wed, Thu)
    best_days = [1, 2, 3]  # Tuesday, Wednesday, Thursday

    calendar = []
    topic_index = 0

    weeks_needed = (len(topics) + posts_per_week - 1) // posts_per_week

    for week in range(weeks_needed):
        week_start = current_date + timedelta(weeks=week)

        # Find posting days this week
        posts_this_week = 0
        for day_offset in range(7):
            if posts_this_week >= posts_per_week or topic_index >= len(topics):
                break

            check_date = week_start + timedelta(days=day_offset)

            # Prefer best days, but use others if needed
            if check_date.weekday() in best_days or posts_this_week < posts_per_week:
                if check_date.weekday() not in [5, 6]:  # Skip weekends
                    calendar.append({
                        "date": check_date.strftime("%Y-%m-%d"),
                        "day": check_date.strftime("%A"),
                        "topic": topics[topic_index],
                        "status": "planned"
                    })
                    topic_index += 1
                    posts_this_week += 1

    return {
        "calendar": calendar,
        "total_posts": len(calendar),
        "weeks": weeks_needed,
        "posts_per_week": posts_per_week,
        "tip": "Best posting times: 9-11 AM and 1-3 PM on weekdays"
    }


def generate_cta(product_type: str, tone: str = "professional") -> dict:
    """
    Generate call-to-action suggestions.

    Args:
        product_type: Type of product/service (saas, ecommerce, service, content)
        tone: Tone of voice (professional, casual, urgent, friendly)

    Returns:
        dict: List of CTA suggestions
    """
    ctas = {
        "saas": {
            "professional": [
                "Start Your Free Trial",
                "Schedule a Demo",
                "Get Started Today",
                "See It in Action",
                "Request a Quote"
            ],
            "casual": [
                "Give It a Try",
                "Jump In - It's Free",
                "See What's Possible",
                "Let's Do This",
                "Take It for a Spin"
            ],
            "urgent": [
                "Start Free - Limited Time",
                "Claim Your Spot Now",
                "Don't Miss Out - Sign Up",
                "Get Instant Access",
                "Limited Spots Available"
            ]
        },
        "ecommerce": {
            "professional": [
                "Shop Now",
                "Add to Cart",
                "Buy Now",
                "Complete Your Purchase",
                "View Collection"
            ],
            "casual": [
                "Grab Yours",
                "Get It Now",
                "Treat Yourself",
                "Make It Yours",
                "Shop the Look"
            ],
            "urgent": [
                "Buy Now - Sale Ends Soon",
                "Limited Stock - Order Now",
                "Flash Sale - Shop Now",
                "Don't Miss Out",
                "Last Chance to Save"
            ]
        },
        "service": {
            "professional": [
                "Book a Consultation",
                "Get in Touch",
                "Request a Quote",
                "Schedule a Call",
                "Learn More"
            ],
            "casual": [
                "Let's Chat",
                "Say Hello",
                "Book a Call",
                "Tell Us Your Needs",
                "Let's Work Together"
            ],
            "urgent": [
                "Book Now - Spots Filling Up",
                "Limited Availability",
                "Schedule Before Spots Fill",
                "Act Now",
                "Reserve Your Spot"
            ]
        },
        "content": {
            "professional": [
                "Download Now",
                "Get the Guide",
                "Access the Resource",
                "Subscribe for Updates",
                "Read More"
            ],
            "casual": [
                "Get Your Copy",
                "Dive In",
                "Join the Community",
                "Stay in the Loop",
                "Check It Out"
            ],
            "urgent": [
                "Download Before It's Gone",
                "Get Instant Access",
                "Subscribe Now",
                "Don't Miss This",
                "Get It Free - Today Only"
            ]
        }
    }

    product_ctas = ctas.get(product_type.lower(), ctas["service"])
    tone_ctas = product_ctas.get(tone.lower(), product_ctas["professional"])

    return {
        "product_type": product_type,
        "tone": tone,
        "suggestions": tone_ctas,
        "tip": "A/B test different CTAs to find what works best for your audience"
    }


def seo_keyword_analysis(keyword: str) -> dict:
    """
    Analyze a keyword for SEO potential (basic analysis).

    Args:
        keyword: Target keyword or phrase

    Returns:
        dict: Keyword analysis with suggestions
    """
    words = keyword.lower().split()
    word_count = len(words)

    # Classify keyword type
    if word_count == 1:
        keyword_type = "Short-tail (head)"
        competition = "Very High"
        recommendation = "Difficult to rank. Consider adding modifiers."
    elif word_count == 2:
        keyword_type = "Medium-tail"
        competition = "High"
        recommendation = "Competitive. Good for established sites."
    elif word_count <= 4:
        keyword_type = "Long-tail"
        competition = "Medium"
        recommendation = "Good balance of search volume and competition."
    else:
        keyword_type = "Very Long-tail"
        competition = "Low"
        recommendation = "Low competition but also lower search volume."

    # Check for commercial intent
    commercial_words = ['buy', 'best', 'top', 'review', 'price', 'cheap', 'deal', 'discount', 'compare']
    has_commercial_intent = any(w in keyword.lower() for w in commercial_words)

    # Check for informational intent
    info_words = ['how', 'what', 'why', 'when', 'where', 'who', 'guide', 'tutorial', 'tips']
    has_info_intent = any(w in keyword.lower() for w in info_words)

    # Determine intent
    if has_commercial_intent:
        intent = "Commercial/Transactional"
        content_type = "Product pages, comparisons, reviews"
    elif has_info_intent:
        intent = "Informational"
        content_type = "Blog posts, guides, tutorials"
    else:
        intent = "Mixed/Navigational"
        content_type = "Landing pages, category pages"

    # Generate related keyword suggestions
    modifiers = ['best', 'top', 'how to', 'guide', 'for beginners', 'vs', 'review', 'tips']
    related = [f"{mod} {keyword}" if mod in ['best', 'top', 'how to'] else f"{keyword} {mod}"
               for mod in modifiers[:5]]

    return {
        "keyword": keyword,
        "word_count": word_count,
        "keyword_type": keyword_type,
        "estimated_competition": competition,
        "search_intent": intent,
        "recommended_content_type": content_type,
        "recommendation": recommendation,
        "related_keywords": related,
        "tip": "Focus on long-tail keywords for newer websites"
    }