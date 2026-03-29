"""
LetterForge — Hacker News "Show HN" submission helper.
Generates the perfect Show HN post and optionally submits via HN API.

HN doesn't have a public posting API — this script opens the submission
URL in your browser pre-filled. Run this once to launch on HN.

Usage:
  python hn_post.py --open
  python hn_post.py --print
"""

import argparse
import urllib.parse
import webbrowser

APP_URL = "https://coverletter-ai.vercel.app"

TITLE = "Show HN: LetterForge – AI cover letter generator that tailors to each job (free, client-side)"

TEXT = """I got frustrated watching friends send the same cover letter to 50 companies and wonder why they got no replies.

So I built LetterForge: paste a job description + your background, pick a tone, get a fully tailored cover letter in ~30 seconds.

Technical details:
- 100% client-side — your data goes directly from your browser to Anthropic's API. I never see it.
- You use your own Anthropic API key (free tier covers dozens of letters)
- Prompt-engineered to: mirror the company's language from the JD, avoid the 15 most ATS-flagged phrases, map specific achievements to their exact requirements, and never output [placeholder] text

The difference from just prompting ChatGPT: the system prompt extracts culture signals, language patterns, and stated values from the job posting, then uses those to frame your experience. The output reads like you actually researched the company.

Live: {url}
GitHub: https://github.com/cosmolotto

Would love feedback from anyone in a job search right now.""".format(url=APP_URL)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--open", action="store_true", help="Open HN submission in browser")
    parser.add_argument("--print", action="store_true", help="Print the post text")
    args = parser.parse_args()

    params = urllib.parse.urlencode({"title": TITLE, "url": APP_URL, "text": TEXT})
    hn_url = f"https://news.ycombinator.com/submitlink?{params}"

    if args.print or not args.open:
        print("=== HACKER NEWS SHOW HN ===")
        print(f"Title: {TITLE}")
        print(f"URL: {APP_URL}")
        print(f"\nText:\n{TEXT}")
        print(f"\nSubmission URL:\n{hn_url}")

    if args.open:
        print("Opening HN submission in browser...")
        webbrowser.open(hn_url)


if __name__ == "__main__":
    main()
