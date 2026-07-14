# SafeHarbor

Catching PHI before it leaks into ChatGPT / Claude / Gemini.

The idea: hospitals can't realistically stop staff from pasting things into
an LLM, so instead of blocking it, sit in the middle as a proxy, look at what
is actually being sent, and strip the protected health information out before
it leaves the network.

## Planned pieces

- a mitmproxy addon that intercepts requests to known AI domains
- a PHI detection engine (regex first, something smarter later)
- a dashboard to see what's going on

Nothing works yet — this is day one.
