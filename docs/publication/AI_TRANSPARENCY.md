# AI transparency and scope

Reviewed on **2026-11-13** for Forever Frost Alert **0.3.1**.

**All project-specific source code was generated exclusively by AI, following the maintainer's instructions.** The maintainer sets the requirements and publishes the project. Documentation and the original project icon were also AI-generated. The icon's generation prompt is recorded in `assets/branding/PROMPT.md`.

This statement concerns this project's code, including its addon, tests and publication scripts. Blizzard's game client, client artwork, GitHub Actions, Python and test dependencies retain their own provenance and licenses. The addon references Blizzard artwork already installed in the client; that artwork is not bundled.

## Current functionality and AI Act assessment

The addon displays an existing player buff using fixed Lua rules and Blizzard UI APIs. It does not contain a machine-learning model, perform model inference, call an AI service or generate synthetic media during use.

Our project-specific assessment is that this functionality does not itself constitute an AI system merely because AI generated its source code. This assessment is based on the definition in [Article 3(1) of the EU AI Act](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-3). [Article 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50) addresses transparency duties for specified AI systems and uses, including direct AI interaction and certain synthetic content. It is not a general certification scheme for software written with AI.

The disclosures record provenance and make the use of AI visible. They are **not a legal opinion, conformity assessment or certification of compliance with all applicable law**. AI-tool providers' obligations and the maintainer's own use of those tools are separate from the addon's runtime functionality. No claim of human editorial review or a statutory exemption is made solely because automated tests pass.

## Publication practice

- Retain the explicit AI-code disclosure in README, short descriptions, CurseForge copy, release notes, announcements and packaged notices.
- Identify generated branding and keep its provenance record. Preserve existing provenance information when exporting or distributing it.
- Keep external code/assets and their licenses distinct from this project's generated code.
- Keep compatibility and testing claims accurate; the release remains a beta pending live-client verification.
- Reassess applicable obligations before adding AI services, AI-generated media features or other materially different functionality. Describe mixed code provenance accurately if future contributions change the exclusively AI-generated status.
