from typing import List
from dataclasses import dataclass, field


@dataclass
class TestCase:
    name: str
    reviews: List[str]
    # Sentiment expectation: True=positive, False=negative, None=mixed/unknown
    expect_positive: bool | None = None
    # Must confidence be low? (< 0.5)
    expect_low_confidence: bool = False
    # Must uncertainty_reason be non-empty?
    expect_uncertainty: bool = False
    # Must both pros and cons be non-empty?
    expect_both_sides: bool = False


TEST_CASES: List[TestCase] = [
    TestCase(
        name="all_positive",
        reviews=[
            "This product is absolutely amazing! Best purchase I've made all year.",
            "Works perfectly, fast delivery, great quality.",
            "My baby loves it. Would buy again without hesitation.",
            "Five stars. Does exactly what it says.",
        ],
        expect_positive=True,
    ),
    TestCase(
        name="all_negative",
        reviews=[
            "Terrible quality. Broke after one day.",
            "Complete waste of money. Do not buy.",
            "Returned it immediately. Very disappointed.",
            "Worst product I've ever bought.",
        ],
        expect_positive=False,
    ),
    TestCase(
        name="mixed_reviews",
        reviews=[
            "Good product but shipping was slow.",
            "Quality is decent, price is a bit high.",
            "Works fine for the price, nothing special.",
            "Love the design but the material feels cheap.",
        ],
        expect_positive=None,
        expect_both_sides=True,
    ),
    TestCase(
        name="empty_input",
        reviews=[],
        expect_low_confidence=True,
        expect_uncertainty=True,
    ),
    TestCase(
        name="noisy_input",
        reviews=["asdfghjkl qwerty 12345 !!!???", "...", "####", "   "],
        expect_low_confidence=True,
        expect_uncertainty=True,
    ),
    TestCase(
        name="short_input",
        reviews=["ok"],
        expect_low_confidence=True,
        expect_uncertainty=True,
    ),
    TestCase(
        name="long_input",
        reviews=[
            "Great product, highly recommend!",
            "Works as described, fast shipping.",
            "My kids love it, very durable.",
            "Good value for money.",
            "Easy to assemble and use.",
            "Bought this as a gift, recipient loved it.",
            "Solid build quality, no complaints.",
            "Arrived on time and well packaged.",
            "Does exactly what it promises.",
            "Would definitely buy again.",
            "Better than expected for the price.",
            "Customer service was helpful too.",
        ],
        expect_positive=True,
    ),
    TestCase(
        name="conflicting_reviews",
        reviews=[
            "Best product on the market! Absolutely love it.",
            "Absolute garbage, never buying again.",
            "Amazing quality, exceeded expectations.",
            "Broke immediately, total waste of money.",
        ],
        expect_positive=None,
        expect_both_sides=True,
    ),
    TestCase(
        name="duplicate_reviews",
        reviews=[
            "Great product, fast shipping!",
            "Great product, fast shipping!",
            "Great product, fast shipping!",
            "Great product, fast shipping!",
        ],
        expect_positive=True,
    ),
    TestCase(
        name="irrelevant_reviews",
        reviews=[
            "The weather today is sunny.",
            "I had pasta for lunch.",
            "My cat knocked over a glass.",
        ],
        expect_low_confidence=True,
        expect_uncertainty=True,
    ),
    TestCase(
        name="multilingual_input",
        reviews=[
            "المنتج رائع جداً وسريع التوصيل",
            "Great product, highly recommend!",
            "جودة ممتازة وسعر مناسب",
            "Excellent quality, worth every penny.",
        ],
        expect_positive=True,
    ),
    TestCase(
        name="edge_case_unclear",
        reviews=["meh", "fine", "ok", "whatever", "I guess"],
        expect_low_confidence=True,
        expect_uncertainty=True,
    ),
]
