# 02: Policy answers with Citations

**What to build:** The Employee asks a Handbook question such as annual leave days. The Coordinator hands off to the Knowledge Agent, which searches Handbook Passages, answers only from them, and ends with a Citation naming the document and heading. When nothing relevant exists it says so instead of guessing. The trace shows the Handoff and the search tool call.

**Blocked by:** 01 Chat skeleton

**Status:** done

- [ ] Three or four short English Handbook documents for a fictional company (leave, IT equipment, expenses, remote work)
- [ ] Retrieval splits documents into Passages at headings, embeds with Gemini, caches vectors on disk keyed by content hash, and returns the top three by cosine with Citations
- [ ] Second startup reuses the cache and makes no embedding calls
- [ ] Knowledge Agent answers with a Citation and hands back to the Coordinator
- [ ] Off-Handbook question gets an honest "not covered" reply
- [ ] Pytest: ranked results with Citations using a fake embedder; cache reuse
