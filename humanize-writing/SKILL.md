---
name: humanize
description: "Use when a draft sounds AI-generated or must not read as AI: 'humanize', 'de-AI', 'make this sound human', 'less AI', 'AI-smooth', 'sounds like ChatGPT', AI-detector concerns, or any external-facing text before delivery. Works as a universal base layer under any personal-voice or brand-voice skill. Language-agnostic."
---

# Humanize

Strip the machine tells from a draft. Stance: authentic writing, never detector tricks. Every rule applies in every language.

## Vocabulary

**Banned AI words.** Use the human alternative:

| AI word | Human | AI word | Human |
|---|---|---|---|
| leverage | use | utilize | use |
| unlock | find, get, build | implement | build, ship, start |
| empower | help | demonstrate | show |
| delve | dig into | subsequently | then |
| foster | build, create | methodology | method |
| robust | strong, solid | endeavor | try |
| holistic | full picture | commence | start |
| nuanced | tricky, specific | approximately | about |
| landscape | market, world, space | sufficient | enough |
| resonate | hit home, clicked | prior to | before |
| comprehensive | full, thorough | in order to | to |
| facilitate | run, organize | with regard to | about |
| optimize (outside eng) | improve, fix | in the event that | if |
| catalyst | trigger, reason | at this point in time | now |
| streamline | simplify, cut | synergy | working together |
| tapestry | mix, mess | thought leadership | what I learned |
| navigate (metaphor) | handle, deal with | deep dive | closer look, breakdown |
| game-changer | what moved the needle | paradigm | way of thinking |

**Banned phrases.** "In today's fast-paced world", "It's worth noting that", "I'm excited to announce", "Let me share", "Here's the thing", "The key takeaway is", "Not only X but also Y", "At the end of the day", "It goes without saying", "Without further ado", "Having said that", "Moving forward", "First and foremost", "Last but not least", "A testament to", "Serves as a reminder", "In an era where", "It's important to remember", "While X, it's important to consider Y", "As someone who", "Imagine a world where", "Picture this".

**Banned transitions.** Furthermore, Moreover, Additionally, That being said, On the flip side, It's also worth considering, Building on that point, This brings us to, With that in mind. Just start the next thought. New paragraph, or "But." on its own line.

**Read-aloud test.** If you wouldn't say the sentence to a colleague over coffee, simplify it.

**No scare quotes.** Quote actual people or use no quotes. "Servant leadership" in quotes is a tell.

## Punctuation and formatting

1. **No em dashes (—) or en dashes (–). Anywhere, any language.** Use period, comma, colon, `+`, or new line. Hyphens in compounds (co-founder) are fine.
2. **No parentheses as asides.** Restructure into a sentence. Parens for citations and URLs only.
3. **No over-formatting.** Social and email: no headers, bold 1-2 phrases max, white space does the structure.
4. **Emojis: one functional pointer or none.** No decoration.
5. **Vary comma cadence.** If most sentences carry exactly one mid-sentence comma, mix in zero-comma sentences, a colon, a fragment. Kill the in-sentence rule of three ("clear, concise, and compelling"): two adjectives or one.

## Structure

- **Openers, kill:** "In today's...", "As a [role], I've learned...", "Have you ever wondered", "[Topic] is one of the most important", "Let me share a story", "I recently had the opportunity", "There's a common misconception". Start mid-story instead: a scene, a number, a claim, a contradiction. Specific from word one.
- **Closers, kill:** "In conclusion", "To sum up", "Remember, the key is", "I'd love to hear your thoughts", "What strategies have worked for you?", "Here's to...", any recap, any optimistic bow. End on a wedge, a punchline, an honest admission, or just stop.
- **Paragraph asymmetry:** no three consecutive paragraphs with the same sentence count. Mix 1-sentence with 3-4-sentence paragraphs. Overall shape lopsided: two long blocks + one short, never n equal headed sections. On social: one thought per line.
- **Lists:** 2 or 4 items over 3 or 5. Items unequal in length and grammar. No bold-header-plus-explanation per item. No alliterative "three pillars" names.

## Statistical tells

- **Burstiness:** sentence lengths must spike and drop. At least one sentence of 6 words or fewer per ~120 words. Flag any draft where most sentences sit in one 10-word band. Over 25 words: read aloud, split unless the length earns it.
- **Predictability:** hide a sentence's last word; if a reader could guess it, swap for the surprising concrete one. Kill stock collocations: "vibrant community", "invaluable insights", "seamless experience", "actionable takeaways", "meaningful impact".
- **Hedging cap:** max 1 hedge per 300 words (might, perhaps, potentially, arguably, "tends to", "can help", "it seems"). Never two in one sentence. No both-sides shrug: pick a side.
- **Specificity:** every "many people / various companies / several leaders / significant growth" becomes a number, name, or date, or gets cut. Never invent one.
- **Honest negativity:** things that sucked stay sucked. No silver linings, no "blessing in disguise". "I don't know" is allowed.
- **One messy detail:** too-clean examples are a tell. "Inherited 30 microservices and almost no docs" beats the perfectly illustrative version.

## Calibration

**AI-smooth (kill):**
> In today's rapidly evolving software landscape, effective code review is more important than ever. By fostering a culture of constructive feedback, teams can unlock significant improvements. In conclusion, code review is not just a process, but a mindset.

**Human:**
> Our code reviews took 4 days. Not because the code was hard. Because nobody wanted to go first.
>
> One change: reviews not picked up by lunch bounce back, author ships behind a flag. Average now: 7 hours. Two people hated it and said so in the retro. First honest retro all year.

## What NOT to do

No evasion tricks: no homoglyphs, no invisible or zero-width characters, no deliberate typos or planted mistakes, no paraphrase-spinning. They break copy, search, and screen readers, and they're dishonest. If a draft only passes because of a trick, it failed. The honest version of imperfection is not over-editing: fragments, starting with And or But.

## Self-verification before delivery

**Grep (each must be zero or fixed):**

1. `—` or `–`
2. Any banned word from the table
3. Any banned phrase or transition
4. `In today's|In an era|As someone who|Have you ever|Let me share|I recently had`
5. `In conclusion|To sum up|I'd love to hear|What strategies|Here's to`
6. `[Mm]any |[Vv]arious |[Ss]everal ` + plural noun
7. Hedges over 1 per 300 words
8. Parens not wrapping a citation or URL
9. Decorative emojis

**Judgment (pass/fail, all must pass):**

10. Burstiness: lengths jump, at least one ultra-short sentence, no clustering
11. Paragraphs uneven; lists (if any) unsymmetric
12. Opens mid-story with a specific; ends with no recap, no bow
13. No guessable endings or stock collocations; one messy real detail present
14. A side is picked; negatives stay negative
15. Read-aloud passes

Below 15/15: fix and re-run, or tell the user exactly which check failed and why it stays.
