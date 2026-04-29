# Reflection

## 1. What are the limitations or biases in this system?

The most significant limitation is **catalog depth**. With 18 songs across 14
genres, most genre+mood combinations have zero or one match. The scoring
function is mathematically sound, but it can only compare against songs that
exist. A metal fan who wants happy music, or a jazz fan who wants energetic
songs, gets recommendations that satisfy at most one of their stated criteria
— not because the algorithm is wrong, but because the catalog was never
designed to serve those tastes.

A closely related bias is **genre-weight loyalty**. In the default
`genre-first` mode, a genre match is worth 3 points out of a maximum 7. That
means a song with a matching genre but completely wrong mood and energy will
beat a song with perfect mood and energy but a different genre, as long as
the energy gap on the second song is larger than 0.67. In practice, this
means Neon Rage — an intense, high-energy metal track — consistently
out-ranks happier, more energy-accurate songs for a user who asked for
happy metal music. The genre string matching is binary (exact or zero), so
there is no way for the system to reason that "indie pop" is closer to "pop"
than "metal" is.

There is also an **energy distribution bias** baked into the catalog itself.
Every happy-mood song in the catalog has energy above 0.76. A user who
prefers calm, low-energy but upbeat music (energy=0.3, mood=happy) will always
receive songs that overshoot their energy target by a wide margin. The scoring
function correctly penalises the mismatch, but the top results still all come
from the same high-energy happy cluster because there is nothing else to choose
from. The system cannot distinguish between "no good match exists" and "here
are the least bad options."

Finally, there is a **filter bubble** effect: because the system uses only
content-based filtering with no collaborative signal, two users with identical
stated preferences will always receive identical recommendations regardless
of what either of them has actually enjoyed or skipped. The system has no
mechanism to learn or adapt.

---

## 2. Could this AI be misused, and how would you prevent that?

A music recommender seems low-stakes, but the design patterns it demonstrates
can be misused in more consequential contexts.

**Catalog manipulation.** Because the recommender ranks only songs in its own
catalog, a commercial deployment could be gamed by populating the catalog with
sponsored or promoted tracks in underserved genres, ensuring they win by
default when no genuine match exists. The classical+melancholic profile
illustrates this: after Sonata No. 3, 2nd and 3rd place are filled by whatever
acoustic, low-energy songs happen to exist — not by the most relevant options.
A platform could exploit this gap to surface content it profits from. The
prevention is transparency: show the user a confidence score or a message like
"limited matches found for this profile" rather than implying all three results
are equally trustworthy.

**Reinforcing narrow taste.** If the system were used in a real product and
users received recommendations only within their stated genre, it would
actively prevent them from discovering music outside that box. Repeated
genre-only filtering can narrow a listener's world over time. Mitigation
strategies include a diversity bonus in scoring (penalising results that are
too similar to each other), or a "wildcard" slot that deliberately surfaces
one cross-genre recommendation per session.

**The RAG explanation layer.** The Claude-powered explanation could be misused
to make a low-confidence recommendation sound authoritative. If Neon Rage is
the only metal song and scores 3.54 out of a possible 7.0, the explanation
could still be written in confident language that a user would trust. The
guardrail in this project — instructing Claude to use only the catalog data
and not invent alternatives — helps, but it does not prevent confident-sounding
language about a weak result. A production system should pass the raw score
and the maximum possible score to the model and instruct it to qualify
low-confidence results explicitly.

---

## 3. What surprised you while testing the system's reliability?

The biggest surprise was how dramatically the scoring mode changed the results
without changing any of the underlying data or user preferences. Running
`genre=metal, mood=happy, energy=0.5` through all three modes produced
three meaningfully different top-3 lists:

- `genre-first` surfaced Neon Rage as #1 even though it matches only 1 of
  3 stated preferences.
- `mood-first` dropped Neon Rage out of the top 3 entirely and replaced it
  with three happy-mood songs from completely different genres.
- `energy-focus` kept the same top 3 as mood-first but changed the score
  distribution, making the energy gap more visible in the numbers.

The mode is essentially a hidden editorial decision about what "best match"
means, and changing it can feel like the system is behaving inconsistently
even though it is doing exactly what the weights specify. A real user shown
two different outputs from the same profile and different modes would likely
conclude the system was unreliable, not that the weights had changed.

The second surprise was the score collapse in niche profiles. The
classical+melancholic profile produced a 1st-place score of 6.98 and a
2nd-place score of 1.92 — a 5-point gap. The system showed all three results
with equal visual weight in the output, implying comparable confidence. Until
the Claude explanation named the drop-off explicitly, there was no way to see
from the output alone that 2nd and 3rd place were essentially random.

The third surprise came from debugging the authentication layer rather than
the recommender itself. The assumption that `ANTHROPIC_API_KEY` would simply
be available in the environment was wrong. Claude Code uses an OAuth token
passed through a close-on-exec file descriptor — meaning child processes
(like the `python3` subprocess running the RAG pipeline) never inherit it.
The fix required understanding the process model at the OS level, not just
the API. The fact that `claude auth status` returned `loggedIn: true` while
every SDK call failed was disorienting until the mechanism was clear.

---

## 4. One instance where AI gave a helpful suggestion, and one where it was flawed

### Helpful: naming the structural failure the scores could not

When the metal+happy+energy=0.5 profile was passed to Claude with the list
of recommended songs, it produced this observation unprompted:

> *"The system split its strategy: one song for genre loyalty, three songs for
> mood compatibility, with energy accuracy sacrificed across the board."*

This was genuinely useful because the scoring output does not say this
anywhere. The rule-based explanation lists which weights fired for each song,
but it does not synthesise across the full result set to explain the pattern.
Claude identified that the recommender was not making one trade-off — it was
making a different trade-off for each result — and that energy was the
consistent loser. That cross-result synthesis is exactly what the RAG layer
was designed to add, and it worked as intended.

### Flawed: confident language about a weak result

When asked about the classical+melancholic profile, Claude described
Spacewalk Thoughts and Rainy Porch (2nd and 3rd place, scores under 2.0)
in terms that sounded like genuine secondary recommendations rather than
near-random fallbacks. Phrases like "compensates with strong acoustic
character" made the result sound like a considered suggestion, when in
reality those songs ranked only because they were acoustic and low-energy —
they share no genre or mood with the user's stated preference at all.

The system prompt said "use only the song catalog" and "do not invent songs,"
which prevented hallucination. But it did not instruct Claude to qualify
results where the score gap was large or where genre and mood both missed.
Claude defaulted to helpful-sounding language because that is the natural
register of a recommendation assistant — it did not know it was supposed to
signal low confidence. The fix would be to include the raw score and the
maximum possible score in the query, and add an explicit instruction: if a
song scores below 30% of the maximum, describe it as a partial or speculative
match rather than a recommendation.
