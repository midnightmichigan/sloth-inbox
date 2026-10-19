"""Sample overnight inbox fixture (fully synthetic — no real email).

Used by run_sloth.py --demo and by test_flow.py. EXPECTED maps each
message id to the category the deterministic classifier must produce.
"""
from __future__ import annotations

FIXTURE_MESSAGES: list[dict] = [
    {
        "id": "m01",
        "sender": "billing@citypower.example",
        "subject": "Payment due: your electric bill",
        "body": "Your electric bill of $84.12 is due Friday. Pay online to avoid a late fee.",
        "date": "2026-10-19T22:14:00",
    },
    {
        "id": "m02",
        "sender": "office@mapleschool.example",
        "subject": "Permission slip needed for field trip",
        "body": "Please sign and return Mia's permission slip by Thursday for the science museum trip.",
        "date": "2026-10-19T21:02:00",
    },
    {
        "id": "m03",
        "sender": "digest@rustweekly.example",
        "subject": "This week in Rust — weekly digest",
        "body": "Top posts this week... Unsubscribe: https://rustweekly.example/unsub",
        "date": "2026-10-19T06:00:00",
        "meta": {"list_unsubscribe": True},
    },
    {
        "id": "m04",
        "sender": "updates@rustweekly.example",
        "subject": "Rust Weekly #88",
        "body": "Issue 88 is out. Manage preferences or unsubscribe at any time.",
        "date": "2026-10-19T06:05:00",
        "meta": {"list_unsubscribe": True},
    },
    {
        "id": "m05",
        "sender": "deals@megamart.example",
        "subject": "FLASH SALE: 40% off everything",
        "body": "Use coupon MEGASLOTH for an extra 10%. Shop now, sale ends Sunday!",
        "date": "2026-10-19T03:44:00",
    },
    {
        "id": "m06",
        "sender": "offers@trailhead.example",
        "subject": "Your exclusive offer ends tonight",
        "body": "Members save 25% on hiking boots. Limited time only.",
        "date": "2026-10-19T02:10:00",
    },
    {
        "id": "m07",
        "sender": "orders@booknook.example",
        "subject": "Order confirmation #48291",
        "body": "Thank you for your purchase! Your receipt is attached.",
        "date": "2026-10-19T23:31:00",
    },
    {
        "id": "m08",
        "sender": "ship@parcelpost.example",
        "subject": "Your package has shipped — tracking number inside",
        "body": "Good news: your order is on its way. Tracking number: 1Z999AA10123456784.",
        "date": "2026-10-20T01:12:00",
    },
    {
        "id": "m09",
        "sender": "notify@friendnet.example",
        "subject": "Alex mentioned you in a comment",
        "body": "Alex mentioned you: 'this sloth meme is so you'",
        "date": "2026-10-19T20:20:00",
    },
    {
        "id": "m10",
        "sender": "notify@friendnet.example",
        "subject": "You have a new follower: @gardenpixie",
        "body": "@gardenpixie started following you.",
        "date": "2026-10-19T19:55:00",
    },
    {
        "id": "m11",
        "sender": "reminders@smileclinic.example",
        "subject": "Reminder: dentist appointment tomorrow at 9",
        "body": "Just a reminder of your appointment tomorrow at 9:00 AM. Reply YES to confirm.",
        "date": "2026-10-19T18:00:00",
    },
    {
        "id": "m12",
        "sender": "priya@examplemail.example",
        "subject": "Checking in — long time no see!",
        "body": "Hey! It's been ages. Coffee sometime next week?",
        "date": "2026-10-19T17:30:00",
    },
    {
        "id": "m13",
        "sender": "uncle.rob@examplemail.example",
        "subject": "Fw: Fw: funny sloth video 🦥",
        "body": "You have GOT to see this little guy eat a leaf. Took him 4 minutes.",
        "date": "2026-10-19T16:12:00",
    },
    {
        "id": "m14",
        "sender": "billing@citywater.example",
        "subject": "Final notice: water bill past due",
        "body": "Your water bill is past due. Pay within 5 days to avoid shutoff.",
        "date": "2026-10-19T22:40:00",
    },
]

EXPECTED: dict[str, str] = {
    "m01": "needs-you",
    "m02": "needs-you",
    "m03": "newsletter",
    "m04": "newsletter",
    "m05": "promo",
    "m06": "promo",
    "m07": "receipt",
    "m08": "receipt",
    "m09": "social",
    "m10": "social",
    "m11": "needs-you",
    "m12": "low",
    "m13": "low",
    "m14": "needs-you",
}
