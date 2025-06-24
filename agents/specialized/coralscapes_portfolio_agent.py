#!/usr/bin/env python3
"""CoralScapes Portfolio Agent

Generates Twitter/X-ready draft posts showcasing coral semantic-segmentation
work done on an NVIDIA Jetson device.

Outputs JSON files to the standard BingiTech `clients/bingitech/content/generated`
folder so that the existing `TwitterAgent` can pick them up for preview &
posting.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config & helpers
# ---------------------------------------------------------------------------

load_dotenv()

# Default local directory where screenshots live
DEFAULT_PORTFOLIO_DIR = Path.home() / "portfolio"

# Content output folder in the expected location
CLIENT_CONTENT_DIR = (
    Path(__file__).parent.parent.parent / "clients" / "bingitech" / "content" / "generated"
)
CLIENT_CONTENT_DIR.mkdir(parents=True, exist_ok=True)


HASH_TAGS = [
    "#CoralReef",
    "#Jetson",
    "#EdgeAI",
    "#MarineScience",
    "#AI4Good",
    "#CoralScapes",
]


class CoralScapesPortfolioAgent:
    """Create tweet drafts and metadata from portfolio images."""

    def __init__(self, portfolio_dir: Path, test_mode: bool = True):
        self.portfolio_dir = portfolio_dir.expanduser().resolve()
        self.test_mode = test_mode

        if not self.portfolio_dir.exists():
            print(f"❌ Portfolio directory not found: {self.portfolio_dir}")
            sys.exit(1)

        print(f"📁 Scanning portfolio directory: {self.portfolio_dir}")
        print(f"💾 Drafts will be saved to: {CLIENT_CONTENT_DIR}")

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def run(self) -> None:
        images = self._collect_images()
        if not images:
            print("⚠️  No new images found – nothing to do.")
            return

        for img_path in images:
            tweet_json = self._create_draft_from_image(img_path)
            self._save_draft(tweet_json)

        print("\n🎉 Draft generation complete! Run `make review-twitter` to preview.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _collect_images(self) -> List[Path]:
        """Return PNG/JPG images that do not yet have a draft JSON file."""
        image_files = [
            p
            for p in self.portfolio_dir.glob("**/*")
            if p.suffix.lower() in {".png", ".jpg", ".jpeg"}
        ]

        drafts_existing = {
            draft["media"]
            for draft in self._existing_drafts()
            if draft.get("media")
        }

        new_images = [p for p in image_files if str(p) not in drafts_existing]
        print(f"🔍 Found {len(new_images)} new images (of {len(image_files)} total)")
        return new_images

    def _existing_drafts(self) -> List[dict]:
        """Return list of already generated drafts to avoid duplicates."""
        drafts: List[dict] = []
        for file_path in CLIENT_CONTENT_DIR.glob("*coralscapes*.json"):
            try:
                with open(file_path, "r") as f:
                    drafts.append(json.load(f))
            except Exception:
                continue
        return drafts

    def _create_draft_from_image(self, img_path: Path) -> dict:
        """Craft the tweet content and JSON draft structure."""
        timestamp = datetime.now().isoformat()

        # Very simple content template – can be enhanced with GPT calls
        img_name = img_path.stem.replace("_", " ")
        content_lines = [
            f"Semantic-segmentation results on {img_name} using an NVIDIA Jetson AGX Orin.",
            "Real-time coral mapping at the edge!",
            " ",
            " ".join(HASH_TAGS),
        ]
        content = "\n".join(content_lines)

        draft = {
            "platform": "twitter",
            "pillar": "coralscapes",
            "status": "draft",
            "created_at": timestamp,
            "content": content[:279],  # safety trim
            "media": str(img_path),
            "alt_text": "Semantic segmentation overlay showing coral structures.",
            "metadata": {
                "source": "coralscapes_portfolio_agent",
                "generated_at": timestamp,
            },
        }
        return draft

    def _save_draft(self, data: dict) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = CLIENT_CONTENT_DIR / f"coralscapes_twitter_{ts}.json"
        with open(out_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Draft saved: {out_file.relative_to(Path.cwd())}")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main() -> None:  # noqa: D401
    import argparse

    parser = argparse.ArgumentParser(description="CoralScapes Portfolio Agent")
    parser.add_argument(
        "--portfolio",
        type=str,
        default=str(DEFAULT_PORTFOLIO_DIR),
        help="Path to directory containing portfolio screenshots/images.",
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="Immediately pass drafts to TwitterAgent for posting (test mode).",
    )
    args = parser.parse_args()

    agent = CoralScapesPortfolioAgent(Path(args.portfolio))
    agent.run()

    if args.post:
        # Defer to existing TwitterAgent for posting/previewing
        try:
            from agents.specialized.twitter_agent import TwitterAgent

            twitter_agent = TwitterAgent(test_mode=True)
            twitter_agent.run_test_posting()
        except ImportError:
            print("❌ Could not import TwitterAgent – ensure dependencies are installed.")
            sys.exit(1)


if __name__ == "__main__":
    main()
