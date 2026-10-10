# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

--- Howard Dining is difficult to track down because they change things almost yearly.

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Howard Dining Hub | Dining locations with addresses, hours and live OPEN/CLOSED status | https://howard.mydininghub.com/en/locations |
| 2 | Howard Dining Hub | Dining Dollars / Mecca Dollars meal plan details (e.g. The Yard) | https://howard.mydininghub.com/en/meal-plans/meal-plan-options?cat=diningdollars-216958 |
| 3 | Howard Dining Hub | Meal plans overview by class year | https://howard.mydininghub.com/en/meal-plans |
| 4 | Howard Auxiliary Services | Where to use the Bison One Card, accepted currencies per location, and 2026–2027 meal plan changes | https://auxiliary.howard.edu/services/bison-one-card/where-use-your-card |
| 5 | Howard Student Affairs (Housing) | Bison One Card and meal plan info for new students | https://studentaffairs.howard.edu/housing/move-in/bison-one-card-meal-plans |
| 6 | Howard Auxiliary Services | Bison One Card mobile apps | https://auxiliary.howard.edu/services/bison-one-card/mobile-apps |
| 7 | Howard Auxiliary Services | Summer programs and summer stay guests | https://auxiliary.howard.edu/services/bison-one-card/summer-programs-and-summer-stay-guests |
| 8 | Howard Auxiliary Services | Bison One Card terms and conditions | https://auxiliary.howard.edu/services/bison-one-card/terms-conditions |
| 9 | Howard Auxiliary Services | Laundry services paid with the Bison One Card | https://auxiliary.howard.edu/services/bison-one-card/laundry |
| 10 | Reddit | r/HowardUniversity posts (top + hot), saved as individual post files | https://www.reddit.com/r/HowardUniversity/ |


---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 256 tokens maximum . Chunks can be shorter because splits prefer natural boundaries.

**Overlap:** 26 tokens (~10% of 256), carried from the end of one chunk into the start of the next. The overlap is word-aligned, so a word is never cut in half.

**Why these choices fit your documents:** Most documents are short paragraphs or single sentences, so 256 tokens usually holds a complete idea (a dining hall's hours or a policy). Splitting is recursive: paragraphs first, then lines, sentences and words, with a hard token cut only as a last resort. Chunks therefore rarely end mid-sentence. The small overlap keeps a fact that straddles a boundary retrievable from either chunk without bloating the index. Boilerplate is stripped by `clean.py` before chunking.

**Final chunk count:** 57 chunks across 33 cleaned documents.

---

## Sample Chunks

<!-- Paste 5 representative chunks from your document collection after running your ingestion pipeline.
     For each chunk, note which source document it came from.
     These must be actual text — not screenshots. -->

| # | Source document | Chunk text |
|---|----------------|------------|
 https://howard.mydininghub.com/en/locations| Chunk 1 | | | Locations & Menus
Enjoy delicious meals, coffee, snacks, and more at these dining locations.
Dining Halls
Restaurants
Coffee
Convenience
All Locations
1867 Café
6th St NW, Washington, DC 20059
Washington, DC 20059
Opens on 9/3 at 8:00AM
CLOSED
Bethune Annex Café
2225 4th Street Northwest
Washington, DC 20059
Dinner 4:00PM-10:00PM
OPEN
Bison Brew
500 Howard Place Northwest
Washington, DC 20059
All Day 8:00AM-8:00PM
OPEN
Blackburn Café
Blackburn Student Center
2397 6th Street Northwest
Washington, DC 20059
Dinner 4:00PM-10:00PM
OPEN
Chick-Fil-A
Blackburn Student Center
2397 6th Street Northwest
Washington, DC 20059
All Day 8:30AM-9:00PM
OPEN
Everbowl
Blackburn Student Center
2397 6th Street Northwest
Washington, DC 20059

https://howard.mydininghub.com/en/meal-plans/meal-plan-options?cat=diningdollars-216958| Chunk 2 | | | drinks—enjoy flexibility, save time, and stay within your budget!
View Mecca Dollar Plans
Which Meal Plan is Right for You? Use our personalized tool to discover the best meal plan to fit your lifestyle.
Find Your Fit
Campus Dining Made Easy
Meal plans come in all shapes and sizes. Check them out and find what fits best for your schedule!
View Meal Plans
Getting Started With a Meal Plan
Make the most of your meal plan with the tips and tools to help you manage.
Your Campus Dining Experience
Discover seamless access to great food and ultimate campus dining convenience.
Discover Howard University Hospitality Services
Enjoy the Perks
Own your mealtime with ease, savings, and budget clarity!
Super Convenient
Swipe, eat, and enjoy. With your meal plan, navigating campus dining has never been simpler - saving you time for what matters most.
Smart Savings
Get more value from every meal. With locked in rates and prepaid convenience, your meal plan makes dining more affordable.
Budget With Ease
Know what you're spending upfront—no surprises, just delicious meals. Enjoy dining without the financial guesswork.
All For You
Connect with your campus community through student events, tastings, and themed menus that make dining more than just a meal.
Only The Best
Enjoy chef-inspired menus featuring fresh, local, and sustainable ingredients, ensuring quality and variety in every bite.
Tools to Thrive

https://auxiliary.howard.edu/services/bison-one-card/where-use-your-card | Chunk 3 | | |  Card Portal.
Bison One Card holders must grant access to family and friends using the
Bison One Card Portal.
a. To utilize the Bison Bucks Account on the Bison One Card, cardholders present their Bison One Card to participating merchants as payment for products and services.
b.
An updated list of participating merchants is available on the
Bison One Card Portal.
c.
Cardholders may not permit another person to use their Bison One Card for purchases or any other reason.
Any remaining monies in the Bison Bucks account that have not been used will be forfeited after a one (1) year period of inactivity on the Bison Bucks account. Bison Bucks are non-refundable
a.
Funds in the Bison Bucks account cannot be transferred to any other Bison One Card account.
a.
Cardholders are responsible for all charges and obligations incurred on their card, and for all funds placed into their account. Cardholders may cancel the card on line at any time by visiting the
Bison One Card Portal
. Then contact the Bison One Card Office immediately.
b.

https://auxiliary.howard.edu/services/bison-one-card/laundry| Chunk 4 | | | Laundry
Laundry facilities are available in each residence hall on campus.
Laundry machines only accept Laundry Points and Bison Bucks for payment. Resident student have a set amount of funds deposited into their Laundry Points account which is accessible with the use of their BisonCard. Students who have exhausted their Laundry Points accounts balance, will need to deposit funds into their Bison Bucks account prior to using the laundry machines.
Laundry Costs
Wash $2.00
Dry $2.00
Johnson Administration Building
2400 6th Street NW, Basement Suite 11
Washington, DC 20059
Phone: 202-806-2109
onecard@howard.edu
Monday – Friday
10 am - 4 pm
Excluding observed holidays (
academic calendar
Accounts
Bison One Card eAccounts
Laundry Points FAQs
When the semester starts, you receive all of your laundry points to be used for that semester.
Laundry points are sufficient for washing your clothes throughout the semester, and the University provides this service at no cost to our students.
If you go beyond two large loads per week, you will need to use Bison Bucks for laundry for the remainder of the semester.

Reddit | Chunk 5 | | | Real cost of living while attending Howard?
Hi guys,
After recieving a response from Howard and talking to their counselor I am a little more encouraged and confident about applying to Howard next year and hopefully getting addmitted.
I'm wondering though, how much is your real cost of living? The cost sheet they have presented me with states 19k A YEAR! But that does not sound realistic at all. So I'd like to hear from those that do not live in dorms, how much is your yearly cost of living? Rent/transport/food/lifestyle...Do you have a car? And if so how much are you paying for parking in and off campus.
Just trying to plan and be prepared. So any additional info/tips you think might be helpful is very welcome.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, run locally. Vectors are stored in a persistent ChromaDB collection (`howard_dining`) configured for cosine similarity. I chose it over my originally planned Gemini Embedding 2 because it is free, needs no API key, runs fast on a laptop, and my chunks (256 tokens max) fit comfortably inside its input limit.

**Production tradeoff reflection:** With cost removed as a constraint, I would weigh accuracy and latency first. MiniLM is small and fast, but it is weak on short, time-sensitive phrases like "right now" and on matching a person's role ("Junior") to a plan name, which is exactly where my retrieval tests missed. A larger or hosted model (for example a Gemini or OpenAI embedding model) would likely do better on that domain-specific wording, and would allow longer chunks because of larger context limits. The costs are API latency, per-call fees, sending text to a third party, and a dependency on the provider's uptime. I would give up multilingual support, since my corpus is English-only. A hybrid approach (keyword search for hours and names, embeddings for meaning) would also help.

---

## Retrieval Test Results

<!-- Run these 3 queries through your retrieval system and record the top returned chunks.
     For at least 2 of the 3, explain why the returned chunks are relevant to the query.
     Results must be text — not screenshots. -->

**Query 1: "What meal plans are available to me as a Junior?"**

Top returned chunks:
#	distance source chunk_idx	preview
- 1	0.3234	3	0	"Meal Plan Overview... Freshmen Meal Plans Living on campus is..."
- 2	0.3872	3	1	"...Which Meal Plan is Right for You?..."
- 3	0.3874	5	5	"...students who live in residence halls that require a meal plan must purchase a specific meal plan (i.e., the Traditional 14). Black..."

Relevance explanation:

--- Relevant? Yes — 1 and 2 are the meal-plan overview page itself, and 3–5 discuss meal plan eligibility and requirements. Gap: none of these actually names which specific plan is for Juniors (that detail — "Eligible for Juniors and Seniors... The Yard" — lives in source 2, which never surfaced. It's a good chunk but semantically closer to "Mecca Dollars" than to "Junior," so the embedding didn't rank it top-5.

**Query 2: "What dining options are open right now?"**

Top returned chunks:
#	distance source chunk_idx	preview

- 1	0.4507	5	5	"...Dining Halls & Meal Plans..."
- 2	0.4590	3	1	"...Campus Dining Made Easy..."
- 3	0.4671	4	2	"...Why were these specific changes made to the meal plan?..."

Relevance explanation:

--- Relevant? Weak. Only result 4 (source 1, the locations page with live OPEN/CLOSED status) actually answers "what's open right now" — and it's ranked 4th, not 1st. Results 1, 2, 3, 5 are about meal-plan mechanics, not live hours. This is a real retrieval miss: "right now" doesn't have a strong semantic anchor for MiniLM, so it's matching on "dining options" generically rather than on the OPEN/CLOSED status content.

**Query 3: "What do people say about food at Blackburn"**

Top returned chunks:
#	distance source chunk_idx	preview


- 1	0.4438	1	0	dining locations list
- 2	0.4537	5	3	vegan/vegetarian options at Blackburn
- 3	0.4603	5	5	Dining Halls & Meal Plans overview

Relevance explanation:

--- Relevant? Not really. All 5 chunks are official Howard-produced content about Blackburn's facilities and offerings — none are actual student opinions. The query asks "what do people say," implying Reddit, but zero Reddit chunks appear in the top 5, and the distances here are noticeably worse than queries 1–2 (0.44–0.58 vs. 0.32–0.43). This confirms the retrieval gap flagged earlier: the corpus's 24 Reddit posts don't happen to mention Blackburn by name, so there's genuinely no matching content to retrieve — this isn't a chunking or embedding failure, it's a corpus coverage gap for that specific evaluation question.

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The system prompt in [generate.py](scripts/generate.py) tells the model to answer from numbered CONTEXT passages only. The key rules are:

1. "Use ONLY information stated in the numbered CONTEXT passages below. Never use outside knowledge, even if you are confident it is correct."
2. "If the CONTEXT does not contain enough information to answer the question, reply with EXACTLY this sentence and nothing else: *I don't have information on that, but if you have any questions about the Bison One Card, feel free to ask!*"
3. "Do not invent a fact, number, name, URL, or policy detail that is not stated in the CONTEXT."
4. Cite supporting passages inline with their bracketed number, e.g. [1] or [2][3].

Structural choices back this up: the top 5 retrieved chunks are formatted as `[n] (source: id) text` in the user message, temperature is 0, and if retrieval returns no chunks at all, the code returns the refusal string without calling the LLM. The model is `openai/gpt-oss-20b` on Groq (the originally planned Llama 4 Scout was removed from Groq's catalog).

**How source attribution is surfaced in the response:** The "Sources" list is built in code from the chunks retrieval actually returned (one entry per source document: source id, description, URL). It is never parsed from the model's text, so it stays accurate even if the model cites wrongly. Inline `[n]` citations from the model appear in the answer body. When the answer is exactly the refusal string, the sources list is left empty so a non-answer is not attached to sources.

---

## Example Responses

<!-- Provide at least 2 grounded responses (query + response + source attribution)
     and 1 out-of-scope query showing your system's refusal.
     All entries must be text — not screenshots. -->

**Grounded response 1**

Query:

Response:

Source attribution:

---

**Grounded response 2**

Query:

Response:

Source attribution:

---

**Out-of-scope query**

Query:

System response (refusal):

---

## Query Interface

<!-- Describe your query interface: what are the input fields, what does the output look like?
     Then provide a complete sample interaction transcript showing a real exchange. -->

**Input fields:** A single free-text question typed at the `>` prompt of the command-line interface ([cli.py](scripts/cli.py)), started with `python3 scripts/cli.py`. Type `quit` or `exit` to stop. Top-k is fixed at 5.

**Output format:** Plain text: the answer (with inline `[n]` citations), then a `Sources:` list with one line per source document in the form `- <source_id>: <description> (<url>)`. Out-of-scope questions return the fixed refusal sentence and no sources.

---

**Sample Interaction Transcript**

<!-- Show a complete query → response exchange as it actually appears in your interface.
     Must be text — not a screenshot. -->

> **User:** 

> **System:** 

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What meal plans are available to me as a Junior?| The Crown Jewel, The Mecca, The Bison and The Yard (source 4 lists all four 2026–2027 plans; source 2 only labels The Yard as "Eligible for Juniors and Seniors") | | | |
| 2 | What dining options are open right now?| Locations marked OPEN on the locations page (source 1), with hours, e.g. Bison Brew, Chick-Fil-A, Everbowl, The Halal Shack. Hours reflect the scrape date, not the live moment. | | | |
| 3 | What do people say about food at BlackBurn?| Student opinions from Reddit about Blackburn food. The Reddit posts in the corpus do not mention Blackburn, so the correct behavior is a refusal. | | | |
| 4 | What resturants that are off campus can I use my MP bucks at?| Meal Plan Bucks work at off-campus partners such as Roaming Rooster and Rush Bowls (source 2). The full partner list was an image and was not ingested, so a complete list is not expected. | | | |
| 5 | Can I only use my Bison One Card for food?| No. It is also the university ID and is accepted at the Campus Store, Campus Connection (printing, mail), library services, and laundry (sources 4, 5, 9). | | | |

The "System response", "Retrieval quality" and "Response accuracy" columns are not filled in yet. I have not been able to run these five questions end to end on my machine, and I will not guess at results.

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "What dining options are open right now?"

**What the system returned:** Retrieval put the locations page (source 1, the only document with OPEN/CLOSED status) in 4th place. The top results were meal-plan chunks ("Dining Halls & Meal Plans", "Campus Dining Made Easy", a meal-plan changes FAQ), with distances of 0.45 to 0.47.

**Root cause (tied to a specific pipeline stage):** This is an embedding and retrieval failure. `all-MiniLM-L6-v2` matched on the general topic "dining options" and gave "right now" almost no weight, so it cannot tell a live-status listing from marketing text about meal plans. Chunking made it worse: the locations page is one long list of repeating blocks (name, address, hours, OPEN), so each chunk has little topical signal for the model to latch onto. Separately, the hours and OPEN/CLOSED flags were captured at scrape time, so even a perfect retrieval would describe the day of the scrape, not the current moment.

**What you would change to fix it:** Chunk the locations page one location per chunk with the name and hours in a consistent sentence ("Chick-Fil-A, Blackburn Student Center, open 8:30AM–9:00PM") so each chunk carries clear meaning. Add a keyword or metadata filter so time-related queries prefer source 1. Re-scrape on a schedule, and show the scrape date in the answer. A stronger embedding model, or a reranker over the top 10 results, would also help.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the Documents and Chunking Strategy sections first forced me to decide on 256-token chunks and a source list before any code existed, so I could hand those sections straight to the AI tool and verify the output against concrete numbers (max 256 tokens per chunk, metadata on every chunk). The architecture diagram also kept the stages separate, which is why ingestion, embedding, retrieval and generation each live in their own script and could be tested one at a time.

**One way your implementation diverged from the spec, and why:** The spec called for Gemini Embedding 2, Claude as the generation model, and a 15% overlap (38 tokens). I ended up with a local `all-MiniLM-L6-v2` model to avoid API cost and latency, Groq's `openai/gpt-oss-20b` for generation, and a 10% overlap (26 tokens). I also never solved the planned challenge of the off-campus partner list being inside an image, which is why that question is weak in testing.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
