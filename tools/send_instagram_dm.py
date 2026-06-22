#!/usr/bin/env python3
"""Step 3b: Send Instagram DM via instagrapi or dry-run fallback."""
import os
import sys

from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
DRY_RUN = not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD


def send_instagram_dm(ig_handle: str, offer: dict):
    if not ig_handle:
        print(f"WARNING: No instagram_handle for customer. Skipping DM.", file=sys.stderr)
        return {"success": False, "error": "No instagram_handle provided"}

    if DRY_RUN:
        print(f"[DRY RUN] Would send Instagram DM:")
        print(f"  from: {INSTAGRAM_USERNAME or '(not set)'}")
        print(f"  to:   {ig_handle}")
        print(f"  text: {offer.get('offer_title', '(no title)')}")
        return {"success": True, "error": ""}

    try:
        from instagrapi import Client
        cl = Client()
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        user_id = cl.user_id_from_username(ig_handle)
        text = f"{offer['offer_title']}\n\n{offer['offer_details']}\n\n{offer['cta_text']}"
        cl.direct_send(text=text, user_ids=[user_id])
        print(f"Instagram DM sent to {ig_handle}")
        return {"success": True, "error": ""}
    except Exception as exc:
        error_msg = str(exc)
        print(f"ERROR sending Instagram DM: {error_msg}", file=sys.stderr)
        return {"success": False, "error": error_msg}


if __name__ == "__main__":
    test_offer = {
        "offer_type": "discount",
        "offer_title": "Test subject",
        "offer_details": "Test body line 1\nTest body line 2",
        "cta_text": "Click here",
    }
    result = send_instagram_dm("testuser", test_offer)
    print(result)
