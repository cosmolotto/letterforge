"""
LetterForge Twitter/X Marketing Bot
Posts daily tips + promotes the tool.

Setup:
  pip install tweepy
  Set env vars: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

Free tier: 1500 tweets/month write access
"""

import os
import tweepy
import random
from datetime import datetime

APP_URL = "https://letterforge.vercel.app"

DAILY_TIPS = [
    "Cover letter tip: Never open with 'I am writing to express my interest in...' — hiring managers read 50 of these a day. Open with your strongest achievement instead. 🎯",
    "Cover letter tip: Copy-paste keywords from the job description into your letter. ATS systems filter by exact phrase match. Tailoring takes 5 minutes and 3x your callback rate.",
    "Most cover letters fail because they're about YOU, not about THEM. Reframe every sentence: not 'I have 5 years of...' but 'Your team would gain someone who...'",
    "The cover letter structure that gets interviews:\n1. Opening: one specific reason you want THIS company\n2. Middle: 2 achievements that map to their requirements\n3. Close: confident ask, not a beg",
    "Job hunting tip: Apply to fewer jobs with better cover letters. 10 tailored applications > 100 generic ones. The math is real.",
    "If your cover letter could be sent to any company, it's not a cover letter — it's a template. Hiring managers can tell in 10 seconds.",
    "Free AI tip for job seekers: Paste the job description into any AI and ask it to 'list the 5 most important qualities this company is looking for.' Then write your letter to those 5 things.",
    "Cover letter length: 3 paragraphs, under 300 words. Every word over 300 reduces your chance of being read. Keep it tight.",
]

PROMO_TWEETS = [
    f"Built something for the job search grind 👇\n\nLetterForge: paste a job description + your background → get a tailored cover letter in 30 seconds.\n\nFree to try, no signup needed.\n\n{APP_URL}",
    f"Stop sending the same cover letter to every company.\n\nLetterForge tailors your letter to each job posting automatically — mirrors their language, maps your achievements to their requirements.\n\nFree: {APP_URL}",
    f"If you're applying to jobs:\n\n→ Generic cover letter = ignored\n→ Tailored cover letter = 3x callbacks\n\nLetterForge writes the tailored one for you in 30s.\n\nFree to use: {APP_URL}",
]

REPLY_HASHTAGS = ["#jobsearch", "#coverletter", "#jobhunting", "#careers", "#hiring"]


def get_client():
    return tweepy.Client(
        consumer_key=os.environ["TWITTER_API_KEY"],
        consumer_secret=os.environ["TWITTER_API_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_SECRET"],
    )


def post_daily_tip(client, dry_run=False):
    # Rotate tips by day of year
    tip_index = datetime.utcnow().timetuple().tm_yday % len(DAILY_TIPS)
    tip = DAILY_TIPS[tip_index]
    tweet = f"{tip}\n\n{APP_URL}"

    print(f"Posting daily tip:\n{tweet}\n")
    if not dry_run:
        resp = client.create_tweet(text=tweet[:280])
        print(f"Posted: https://twitter.com/i/web/status/{resp.data['id']}")
    else:
        print("[DRY RUN] Would post above tweet.")


def post_promo(client, dry_run=False):
    # Post a promo tweet (run weekly)
    tweet = random.choice(PROMO_TWEETS)
    print(f"Posting promo:\n{tweet}\n")
    if not dry_run:
        resp = client.create_tweet(text=tweet[:280])
        print(f"Posted: https://twitter.com/i/web/status/{resp.data['id']}")
    else:
        print("[DRY RUN] Would post above tweet.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["tip", "promo"], default="tip")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = get_client()

    if args.mode == "tip":
        post_daily_tip(client, dry_run=args.dry_run)
    elif args.mode == "promo":
        post_promo(client, dry_run=args.dry_run)
