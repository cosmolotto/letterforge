"""
LetterForge Reddit Marketing Bot
Monitors job-hunting subreddits and posts helpful content.
Run manually or via GitHub Actions cron.

Setup:
  pip install praw requests
  Set env vars: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
"""

import os
import praw
import time
import json
import random
from datetime import datetime, timedelta

APP_URL = "https://coverletter-ai.vercel.app"
APP_NAME = "LetterForge"

# Subreddits to monitor for cover letter questions
MONITOR_SUBS = [
    "resumes",
    "jobs",
    "careerguidance",
    "cscareerquestions",
    "jobsearchhacks",
    "recruitinghell",
]

# Subreddits for weekly Show & Tell posts
PROMO_SUBS = [
    "SideProject",
    "entrepreneur",
    "startups",
    "indiehackers",
]

# Keywords that signal someone needs a cover letter tool
TRIGGER_KEYWORDS = [
    "cover letter",
    "cover letters",
    "struggling with cover letter",
    "cover letter help",
    "write a cover letter",
    "cover letter template",
    "how to write cover letter",
    "no callbacks",
    "no interview",
    "not getting interviews",
    "application response",
]

HELPFUL_REPLIES = [
    """Great question. A few things that actually move the needle on cover letters:

1. Mirror the job description's exact language (ATS systems love this)
2. Open with a specific achievement, not "I am writing to express..."
3. Mention one thing about the company that shows you actually researched them

If you want to skip the manual work, I built a free tool called {app} that does this automatically — you paste the JD + your background and it generates a tailored letter in ~30 seconds. Works with any industry.

{url}

No signup needed, just bring your own free Anthropic API key.""",

    """The biggest mistake I see on cover letters: they're generic. Same letter, every company.

What gets callbacks is when your letter reads like it was written specifically for *that* job. Reference their tech stack, mention a recent company announcement, map your exact experience to their requirements.

I made a tool to do this automatically: {app} ({url}). You paste the job posting and your background, pick your tone (professional/conversational/bold), and get a tailored letter in 30 seconds. Free to try.""",

    """Cover letters that work have three things:
- Specific company research (not "your company is a leader in...")
- Your achievement mapped to their exact need
- An opening line that isn't "I am writing to apply for..."

I built {app} to handle all of this — it uses AI to read the job posting and generate a letter that mirrors the company's language. Free to use: {url}""",
]

WEEKLY_POST_TITLE = [
    "I built a free AI cover letter generator that actually tailors to each job — Show HN style",
    "Made a tool that turns job description + your background into a tailored cover letter in 30s [free]",
    "[Side Project] LetterForge — AI cover letter generator, free to use",
]

WEEKLY_POST_BODY = """**The problem:** Generic cover letters get ignored. Writing a tailored one for every application takes forever.

**What I built:** LetterForge — paste any job description + your background, choose a tone (Professional / Conversational / Bold), and get a fully tailored cover letter in ~30 seconds.

**How it works technically:**
- Pure frontend, no backend — your data never leaves your browser
- Uses Anthropic's Claude API (you bring your own free API key)
- Prompt-engineered to mirror company language, avoid ATS-flagged phrases, and map your specific achievements to their requirements

**Why it's different from just using ChatGPT:**
The prompt specifically instructs the AI to: extract the company's culture/language from the JD, avoid the 15 most-flagged ATS phrases, and never use placeholder brackets [like this].

**Try it:** {url}

Happy to answer questions. The whole thing is open source on GitHub: https://github.com/cosmolotto

---
*Would love feedback from anyone actively job hunting.*"""


def get_reddit_client():
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        username=os.environ["REDDIT_USERNAME"],
        password=os.environ["REDDIT_PASSWORD"],
        user_agent=f"{APP_NAME}/1.0 by u/{os.environ['REDDIT_USERNAME']}",
    )


def already_replied(post_id, log_file="replied.json"):
    try:
        with open(log_file) as f:
            replied = json.load(f)
        return post_id in replied
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def log_reply(post_id, log_file="replied.json"):
    try:
        with open(log_file) as f:
            replied = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        replied = {}
    replied[post_id] = datetime.utcnow().isoformat()
    with open(log_file, "w") as f:
        json.dump(replied, f, indent=2)


def is_relevant(post):
    text = (post.title + " " + (post.selftext or "")).lower()
    return any(kw in text for kw in TRIGGER_KEYWORDS)


def monitor_and_reply(reddit, dry_run=False):
    replied_count = 0
    for sub_name in MONITOR_SUBS:
        sub = reddit.subreddit(sub_name)
        print(f"Scanning r/{sub_name}...")
        for post in sub.new(limit=25):
            if already_replied(post.id):
                continue
            if not is_relevant(post):
                continue
            # Don't reply to posts older than 6 hours
            age_hours = (time.time() - post.created_utc) / 3600
            if age_hours > 6:
                continue

            reply = random.choice(HELPFUL_REPLIES).format(app=APP_NAME, url=APP_URL)
            print(f"\n[r/{sub_name}] Relevant post: {post.title[:80]}")
            if not dry_run:
                post.reply(reply)
                log_reply(post.id)
                replied_count += 1
                time.sleep(30)  # Reddit rate limit
            else:
                print(f"[DRY RUN] Would reply:\n{reply[:200]}...")
                log_reply(post.id)

    print(f"\nReplied to {replied_count} posts.")
    return replied_count


def post_weekly_promo(reddit, dry_run=False):
    """Post a weekly Show & Tell to relevant subreddits."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = "promo_log.json"

    try:
        with open(log_file) as f:
            promo_log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        promo_log = {}

    # Only post once per week per subreddit
    week = datetime.utcnow().strftime("%Y-W%W")
    posted = 0

    for sub_name in PROMO_SUBS:
        key = f"{sub_name}:{week}"
        if key in promo_log:
            print(f"Already posted to r/{sub_name} this week, skipping.")
            continue

        title = random.choice(WEEKLY_POST_TITLE)
        body = WEEKLY_POST_BODY.format(url=APP_URL)

        print(f"\nPosting to r/{sub_name}: {title[:60]}...")
        if not dry_run:
            sub = reddit.subreddit(sub_name)
            sub.submit(title, selftext=body)
            promo_log[key] = today
            with open(log_file, "w") as f:
                json.dump(promo_log, f, indent=2)
            posted += 1
            time.sleep(60)
        else:
            print(f"[DRY RUN] Would post to r/{sub_name}")
            promo_log[key] = today
            with open(log_file, "w") as f:
                json.dump(promo_log, f, indent=2)

    print(f"\nPosted to {posted} subreddits.")
    return posted


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["monitor", "promo", "both"], default="monitor")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    reddit = get_reddit_client()
    print(f"Logged in as: {reddit.user.me()}")

    if args.mode in ("monitor", "both"):
        monitor_and_reply(reddit, dry_run=args.dry_run)

    if args.mode in ("promo", "both"):
        post_weekly_promo(reddit, dry_run=args.dry_run)
