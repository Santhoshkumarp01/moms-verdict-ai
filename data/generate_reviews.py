"""
Synthetic product review generator for baby/mother products.
Generates up to 200 reviews with a realistic distribution:
  - 40% positive
  - 30% negative
  - 20% neutral
  - 10% noisy / irrelevant
No external APIs — fully local generation using templates + randomness.
"""

import random
from typing import List

# ─── Product categories ───────────────────────────────────────────────────────

PRODUCTS = [
    "diaper", "baby lotion", "feeding bottle", "baby toy", "baby wipes",
    "baby shampoo", "nursing pillow", "baby monitor", "stroller", "baby carrier",
    "teething ring", "baby food", "baby blanket", "baby powder", "breast pump",
]

# ─── Sentence building blocks ─────────────────────────────────────────────────

POSITIVE_OPENERS = [
    "Really happy with this {product}.",
    "This {product} is absolutely wonderful.",
    "Bought this {product} for my baby and love it.",
    "Best {product} I've ever used.",
    "So glad I found this {product}.",
    "My baby loves this {product}.",
    "This {product} exceeded my expectations.",
    "Highly recommend this {product} to all moms.",
    "Amazing {product}, worth every penny.",
    "This {product} has been a lifesaver.",
]

POSITIVE_DETAILS = [
    "Very soft and gentle on baby's skin.",
    "No leaks at all, even overnight.",
    "Easy to use and clean.",
    "Great quality for the price.",
    "Fast delivery and well packaged.",
    "My newborn took to it immediately.",
    "Durable and well made.",
    "Smells great and feels natural.",
    "Perfect size for a newborn.",
    "Works exactly as described.",
    "My pediatrician recommended it.",
    "No irritation or rashes.",
    "Holds up really well after multiple washes.",
    "Very comfortable for long use.",
    "The design is thoughtful and practical.",
]

POSITIVE_CLOSERS = [
    "Will definitely buy again.",
    "Already ordered a second one.",
    "Five stars without hesitation.",
    "Would recommend to every new mom.",
    "A must-have for any baby.",
    "Couldn't be happier with this purchase.",
    "My go-to brand from now on.",
]

NEGATIVE_OPENERS = [
    "Very disappointed with this {product}.",
    "Would not recommend this {product}.",
    "This {product} did not work for us.",
    "Regret buying this {product}.",
    "Terrible experience with this {product}.",
    "This {product} is a waste of money.",
    "Had high hopes but this {product} let me down.",
    "Returned this {product} after one use.",
    "My baby hated this {product}.",
    "Do not buy this {product}.",
]

NEGATIVE_DETAILS = [
    "Caused a rash on my baby's skin.",
    "Leaked after just a few hours.",
    "Broke after one week of use.",
    "The material feels very cheap.",
    "Strong chemical smell that wouldn't go away.",
    "Completely different from the photos.",
    "Way too small for the size listed.",
    "My baby refused to use it.",
    "The strap broke on the first day.",
    "Packaging was damaged on arrival.",
    "Ingredients caused an allergic reaction.",
    "Stopped working after a month.",
    "Very hard to clean properly.",
    "The lid doesn't seal properly.",
    "Much lower quality than expected.",
]

NEGATIVE_CLOSERS = [
    "Asking for a refund.",
    "One star is too generous.",
    "Save your money and look elsewhere.",
    "Very frustrating experience.",
    "Will not be purchasing again.",
    "Contacted customer support but no help.",
    "Switched to a different brand immediately.",
]

NEUTRAL_TEMPLATES = [
    "The {product} is okay, nothing special.",
    "It does the job but I expected more from this {product}.",
    "Average {product}. Works fine but not outstanding.",
    "The {product} is decent for the price.",
    "Not bad, not great. The {product} is just okay.",
    "The {product} arrived on time. Quality is acceptable.",
    "I've used better {product}s but this one is fine.",
    "The {product} works as expected, nothing more.",
    "Neutral on this {product}. Might try another brand next time.",
    "The {product} is functional but lacks quality finishing.",
    "It's a basic {product}. Does what it says, no extras.",
    "My baby doesn't seem to mind the {product}, so I guess it's fine.",
    "The {product} is alright. I wouldn't go out of my way to recommend it.",
]

NOISY_TEMPLATES = [
    "asdfghjkl qwerty 12345 !!!???",
    "...",
    "####",
    "BUY NOW!!! BEST DEAL EVER!!! CLICK HERE!!!",
    "LIMITED OFFER 50% OFF!!!",
    "The weather today is sunny.",
    "I had pasta for lunch.",
    "My cat knocked over a glass.",
    "Not sure what to write here.",
    "Testing 1 2 3",
    "N/A",
    ".",
    "ok",
    "fine",
    "meh",
    "whatever",
    "I don't know",
    "Lorem ipsum dolor sit amet",
    "This is not a review",
    "???",
]


# ─── Generator ────────────────────────────────────────────────────────────────

def _positive_review() -> str:
    """Build a positive review from randomized template parts."""
    product = random.choice(PRODUCTS)
    opener = random.choice(POSITIVE_OPENERS).format(product=product)
    detail = random.choice(POSITIVE_DETAILS)
    # 60% chance to add a closing sentence
    closer = random.choice(POSITIVE_CLOSERS) if random.random() < 0.6 else ""
    parts = [opener, detail] + ([closer] if closer else [])
    return " ".join(parts)


def _negative_review() -> str:
    """Build a negative review from randomized template parts."""
    product = random.choice(PRODUCTS)
    opener = random.choice(NEGATIVE_OPENERS).format(product=product)
    detail = random.choice(NEGATIVE_DETAILS)
    closer = random.choice(NEGATIVE_CLOSERS) if random.random() < 0.6 else ""
    parts = [opener, detail] + ([closer] if closer else [])
    return " ".join(parts)


def _neutral_review() -> str:
    """Build a neutral review from a single template."""
    product = random.choice(PRODUCTS)
    return random.choice(NEUTRAL_TEMPLATES).format(product=product)


def _noisy_review() -> str:
    """Return a noisy or irrelevant string."""
    return random.choice(NOISY_TEMPLATES)


def generate_reviews(n: int = 200) -> List[str]:
    """Generate n synthetic product reviews with a realistic distribution.

    Distribution:
        - 40% positive
        - 30% negative
        - 20% neutral
        - 10% noisy / irrelevant

    Args:
        n: Number of reviews to generate (default 200).

    Returns:
        List of review strings, shuffled randomly.
    """
    n_positive = int(n * 0.40)
    n_negative = int(n * 0.30)
    n_neutral  = int(n * 0.20)
    # Remainder goes to noisy to ensure total == n
    n_noisy    = n - n_positive - n_negative - n_neutral

    reviews = (
        [_positive_review() for _ in range(n_positive)] +
        [_negative_review() for _ in range(n_negative)] +
        [_neutral_review()  for _ in range(n_neutral)]  +
        [_noisy_review()    for _ in range(n_noisy)]
    )

    random.shuffle(reviews)
    return reviews


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    reviews = generate_reviews(200)
    print(f"Generated {len(reviews)} reviews\n")
    print("Sample (first 10):")
    for i, r in enumerate(reviews[:10], 1):
        print(f"  {i:02d}. {r}")
