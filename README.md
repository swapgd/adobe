# Creative Automation Pipeline (POC)

This proof-of-concept automates creative asset generation for social ad campaigns using **OpenAI Images API**, with **brand compliance checks, legal guardrails, and reporting**.

## Features
- Reads campaign briefs (`brief.json`).
- Uses existing assets if available, otherwise generates new ones with OpenAI.
- Produces creatives in **3 aspect ratios**
- Overlays campaign messages on assets.
- Adds brand logo and verifies brand colors.
- Runs legal content checks (flags prohibited words).
- Logs all results (PASS/FAIL/ERROR) to `outputs/pipeline_log.csv`.

## Setup
1. Clone this repo
2. `cd adobe`
3. export OPENAI_API_KEY="Your OpenAI API Key"
4. Install dependencies:
   pip install -r requirements.txt
5. python pipeline.py
