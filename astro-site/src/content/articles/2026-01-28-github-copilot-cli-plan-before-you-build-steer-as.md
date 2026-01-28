---
title: "GitHub Copilot CLI: Plan before you build, steer as you go"
title_vi: ""
source: "GitHub Changelog"
url: "https://github.blog/changelog/2026-01-21-github-copilot-cli-plan-before-you-build-steer-as-you-go"
topic: "github"
date: "2026-01-28"
excerpt: "GitHub Copilot CLI continues to push the boundaries of agentic AI assistance in your terminal. This week brings powerful new reasoning models, intelligent workflow features that let you steer..."
excerpt_vi: ""
number: 10
publishDate: "2026-01-28T00:00:00Z"
---

GitHub Copilot CLI continues to push the boundaries of agentic AI assistance in your terminal. This week brings powerful new reasoning models, intelligent workflow features that let you steer conversations in real-time, and tighter integration with the GitHub CLI. Here’s what’s new.

![A terminal showing the Copilot CLI interface in plan mode with text indicating that it's in plan mode.](https://github.com/user-attachments/assets/e196c826-d333-4622-954a-e844403daebe)

One of your most requested features is here: **plan mode** gives you a collaborative planning experience before Copilot starts implementing.

Press **Shift + Tab** to cycle in and out of plan mode. In plan mode, Copilot analyzes your request, asks clarifying questions to understand scope and requirements, and builds a structured implementation plan before writing any code.

The experience is conversational. Copilot uses the new `ask_user` tool to prompt you with follow-up questions, confirm assumptions about feature scope, and get your input on design decisions. Once you’re aligned on the approach, you can review the plan in a dedicated panel and tell Copilot to start implementing.

![A terminal window where Copilot asks a clarifying question to the user and provides a list of possible options.](https://github.com/user-attachments/assets/b09388d5-8984-471e-a272-258ad0a84281)

This helps you:

- Catch misunderstandings early before code is written.
- Make informed decisions about implementation approach.
- Stay in control of complex multistep tasks.

![The Copilot CLI interface presenting a list of options (Low, Medium, High, Extra High) for configuring the reasoning effort of GPT-5.2-Codex.](https://github.com/user-attachments/assets/561bdf3e-66b2-4c75-8b1d-1deecc605b8d)

- **GPT-5.2-Codex:** The latest Codex model optimized for code generation and understanding is now available. Select it with `/model` or `--model gpt-5.2-codex`.
- **Configurable reasoning effort:** For GPT models that support extended thinking, you can now configure how much reasoning effort the model applies to your prompts. This lets you balance response speed with reasoning depth depending on your task.
- **Toggle reasoning visibility:** Press **Ctrl + T** to show or hide the model’s reasoning steps during generation. This setting persists across sessions, so you can always see how Copilot approaches complex problems.

![An example of the experience for providing inline feedback on tool call rejection.](https://github.com/user-attachments/assets/ca6d6919-8c83-48ba-a8b2-166ca00fc66a)

- **Enqueue additional messages:** You can now interact with Copilot while it’s thinking. Send follow-up messages to steer the conversation in a different direction, or queue additional instructions for Copilot to process after it finishes its current response. This makes conversations feel more natural and keeps you in control.
- **Inline feedback on rejection:** When you reject a tool permission request, you can give Copilot inline feedback about the rejection so it can adapt its approach without stopping entirely. This makes the conversation flow more naturally when you want to guide Copilot away from certain actions.

Prefix any prompt with `&` to delegate it to the GitHub Copilot coding agent in the cloud (equivalent to the `/delegate` command). This frees up your terminal for other work while Copilot handles longer tasks asynchronously.

- **Auto-compaction:** When your conversation approaches 95% of the token limit, Copilot now automatically compresses your history in the background without interrupting your workflow. This enables virtually infinite sessions.
- **Manual control:** Use `/compact` to manually compress context anytime. Press **Escape** to cancel if you change your mind.
- **Visualize usage:** The `/context` command shows detailed token usage breakdown so you can understand how your context window is being used.

- **Approve parallel requests:** Selecting **approve for session** now auto-approves any pending parallel permission requests of the same type, reducing interruptions during complex multistep operations.
- **Convenience flags:** New `--allow-all` and `--yolo` flags enable all permissions at once for when you trust Copilot to run freely.

![A response from Copilot in the CLI in response to a review request, marking out five security issues and asking if the user wants to have Copilot fix them.](https://github.com/user-attachments/assets/a8d6c4e4-409e-4bb9-ba80-e31a19c7a898)

The new `/review` command analyzes code changes directly in the CLI. Get feedback on your staged or unstaged changes without leaving the terminal—perfect for a quick sanity check before committing.

Copilot can now remember important facts about your codebase across sessions. As you work, Copilot stores conventions, patterns, and preferences it learns, making future sessions more productive. The memory storage tool captures context like coding standards, project structure insights, and your preferred approaches. For more information on Copilot’s agentic memory capabilities, check out [our engineering blog post on Copilot memory](https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/).

- **History filtering:** Shell mode history navigation (`!` prefix) now filters by prefix. Typing `!git` and pressing the up arrow cycles only through previous git commands, making it faster to find and rerun specific commands.
- **Cleaner environment:** Copilot excludes shell commands from your Bash and PowerShell history files, keeping your shell history clean.

- **`/resume` command:** Switch between local and remote GitHub Copilot coding agent sessions easily.
- **`/cd` alias:** Shorthand for `/cwd` to change the working directory.
- **Improved session events:** More concise and visually clean session messages.
- **Tab title:** Current intent now displays in your terminal tab title.
- **Custom instructions:** All custom instruction files now combine instead of using priority-based fallbacks.
- **Redesigned header:** Fresh CLI header with branded mascot and streamlined welcome message.

GitHub CLI users can more easily get started using GitHub Copilot CLI by running `gh copilot`. Running the command for the first time prompts you to install Copilot CLI, and from then on you can use `gh copilot` as a convenient entry point. This works seamlessly in GitHub Actions too—installation happens automatically without confirmation prompts.

Update with your package manager (`brew upgrade copilot-cli`, `winget upgrade GitHub.Copilot`), run `npm install -g @github/copilot@latest`, or let auto-update handle it.

Join the discussion in [Copilot CLI’s public repository](https://github.com/github/copilot-cli).
