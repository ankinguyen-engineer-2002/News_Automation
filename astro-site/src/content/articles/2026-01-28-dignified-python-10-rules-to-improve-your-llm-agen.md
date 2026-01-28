---
title: "Dignified Python: 10 Rules to Improve your LLM Agents Writing Python"
title_vi: ""
source: "Dagster Blog"
url: "https://dagster.io/blog/dignified-python-10-rules-to-improve-your-llm-agents"
topic: "analytics-engineering"
date: "2026-01-28"
excerpt: "Modern LLMs are trained on an enormous and unruly mix of code: questionable StackOverflow snippets, half-finished projects, and hobbyist repositories. When agents generate code from that background,..."
excerpt_vi: ""
number: 4
publishDate: "2026-01-28T00:00:00Z"
---

# Dignified Python

Modern LLMs are trained on an enormous and unruly mix of code: questionable StackOverflow snippets, half-finished projects, and hobbyist repositories. When agents generate code from that background, the results can be fast but unfocused. Even when you don’t fully defer to them, the constant cycle of nudging, correcting, and rewriting can make development feel fragmented rather than cohesive.

At Dagster, intent has always mattered. The platform was built so engineers never have to guess what a system is doing or why it behaves the way it does. As we’ve adopted agent-assisted development, we’ve seen the same need emerge in code generation. LLMs are excellent at reproducing patterns, but they rarely understand the principles that make a codebase feel deliberate and unified.

Python’s flexibility amplifies this problem. There are often many valid ways to solve the same problem, and without guidance an LLM will default to whichever pattern it has seen most often. The result is code that technically works, but feels inconsistent. And can lead to a codebase that feels like it is authors with very different philosophies.

To address this, we codified our opinions about how Python should be written into a set of rules we call Dignified Python. Rather than relying on post-hoc cleanup through reviews or rewrites, we load these rules directly into the model’s context from the start. This gives agents a clear sense of our standards, conventions, and design philosophy.

By encoding intent upfront, we get the speed benefits of LLMs without sacrificing the clarity and consistency that make a shared codebase feel like a single system.

## Why Intent Matters

At Dagster we have strong opinions about how Python should be written. Historically we enforced these through linting and code reviews, but as agents have become more ingrained in our workflows we have codified a set of rules that we can supply directly as context when working with an agent. We refer to these rules as "Dignified Python."

Python's flexibility is one of its greatest strengths, but that flexibility becomes a liability when agents are involved. There are often many valid ways to accomplish the same task, and without guidance an LLM will pick whichever pattern it has seen most frequently. The result is inconsistent code that feels like it was written by a dozen different people with a dozen different philosophies.

Being opinionated cuts through this. By defining clear guidelines and loading them into Claude's context, we have drastically accelerated our engineering velocity while maintaining the quality and consistency of our codebase. The key insight is that you must impart your expertise to the model. An LLM has no understanding of your team's conventions, your architectural decisions, or the hard-won lessons that shaped your codebase. By encoding that expertise into rules, you ensure the AI produces code that reflects your standards rather than generic patterns.

The goal of Dignified Python is not just to generate code that works, it is to generate code that communicates intent. That is where LLMs often fall short. Models are excellent at reproducing patterns, but far less adept at expressing the design principles behind them. Intent is not about choosing the right snippet; it is about applying a coherent philosophy for how Python should be used. Our rules ensure that the code produced by agents reflects that philosophy.

## Ten Rules from Our Claude Prompt

Below are ten rules extracted from the prompt we supply to Claude Code. They reflect Dagster's engineering judgment about how Python should be written, and they are battle-tested against a large, actively maintained codebase. We share them here so you can adopt or adapt them for your own workflows. The goal is simple: impart your expertise to the model so its output reflects your team's standards, not generic patterns from its training data.

### 1. Look Before You Leap

The single most important rule in Dignified Python is to check conditions proactively rather than relying on exceptions for control flow. We call this Look Before You Leap (LBYL), in contrast to the Easier to Ask for Forgiveness than Permission (EAFP) pattern that many LLMs default to.

```
# WRONG: Exception as control flow
try:
 value = mapping[key]
 process(value)
except KeyError:
 pass

# CORRECT: Check first
if key in mapping:
 value = mapping[key]
 process(value)
```

LBYL makes intent explicit. The reader can see immediately what conditions are being checked and what happens in each case. EAFP obscures this by burying the logic inside exception handlers.

Exceptions are still acceptable at error boundaries, when interacting with third-party APIs that provide no alternative, or when adding context before re-raising. A good example is interacting with external services where we lack control over the underlying behavior:

```
# ACCEPTABLE: Third-party API forces exception handling
def _get_bigquery_sample(sql_client, table_name):
 """
 BigQuery's TABLESAMPLE doesn't work on views.
 There's no reliable way to determine a priori whether
 a table supports TABLESAMPLE.
 """
 try:
 return sql_client.run_query(f"SELECT * FROM {table_name} TABLESAMPLE...")
 except Exception:
 return sql_client.run_query(f"SELECT * FROM {table_name} ORDER BY RAND()...")
```

### 2. Never Swallow Exceptions

A common issue that arises from LLM pattern matching is silent error swallowing. Many models overuse broad try and except blocks, and one of the most problematic variants is catching every exception and ignoring it entirely.

```
# WRONG: Silent exception swallowing
try:
 risky_operation()
except:
 pass

# CORRECT: Let exceptions bubble up
risky_operation()
```

`‍`Although the first version will run, it hides failures that may be critical to the correctness of your system. Debugging issues introduced by swallowed exceptions can be extremely difficult since the original error is lost and the failure often surfaces far away from the root cause. The Python community has long discussed restricting or discouraging bare except clauses, as seen in proposals like [PEP 760](https://peps.python.org/pep-0760/).

Dignified Python encourages code that is explicit. If an operation can fail in a meaningful way, that failure should be visible and actionable. That means allowing exceptions to propagate naturally unless there is a compelling and clearly defined reason to handle them.

### 3. Magic Methods Must Be O(1)

Performance is an area where agents often fall short. LLMs tend to focus on producing code that works, not code that is efficient. Without explicit guidance, they may introduce subtle performance issues that only become visible once the code is used at scale.

Magic methods **like\_\_l**en\_\_, **\_\_bool\_\_**, and **\_\_contains\_\_** are called frequently and implicitly. They must run in constant time.

```
# WRONG: __len__ doing iteration
def __len__(self) -> int:
 return sum(1 for _ in self._items)

# CORRECT: O(1) __len__
def __len__(self) -> int:
 return self._count
```

`‍`The first implementation is correct but inefficient. Each call requires iterating over the entire collection, which can introduce significant overhead when used in loops, conditionals, or membership checks. The same rule applies to properties, which should never perform I/O or expensive computation.

### 4. Check Existence Before Resolution

When working with pathlib, LLMs often forget that certain methods can fail on non-existent paths. The rule is simple: always check **.exists()** before calling **.resolve()** or **.is\_relative\_to()**.

```
from pathlib import Path

# WRONG: resolve() can raise OSError on non-existent paths
wt_path_resolved = wt_path.resolve()
if current_dir.is_relative_to(wt_path_resolved):
 current_worktree = wt_path_resolved

# CORRECT: Check exists() first
if wt_path.exists():
 wt_path_resolved = wt_path.resolve()
 if current_dir.is_relative_to(wt_path_resolved):
 current_worktree = wt_path_resolved
```

`‍`This follows directly from the LBYL principle. Instead of catching exceptions after the fact, we verify preconditions before calling methods that might fail.

### 5. Defer Import-Time Computation

Module-level code runs when the module is imported. Side effects at import time cause slower startup, test brittleness, circular import issues, and unpredictable behavior based on import order.

```
from pathlib import Path
from functools import cache

# WRONG: Path computed at import time
SESSION_FILE = Path("scratch/current-session-id")

# CORRECT: Defer with @cache
@cache
def _session_file_path() -> Path:
 """Return path to session ID file (cached after first call)."""
 return Path("scratch/current-session-id")
```

`‍`The **@cache** decorator ensures the computation happens only once, but not until the function is first called. This pattern works for any resource initialization: configuration loading, database connections, or path construction.

### 6. Verify Your Casts at Runtime

**typing.cast()** is a compile-time only construct. It tells the type checker to trust you but performs no runtime verification. If your assumption is wrong, you will get silent misbehavior instead of a clear error.

```
from typing import Any, cast
from collections.abc import MutableMapping

# WRONG: Blind cast
cast(dict[str, Any], doc)["key"] = value

# CORRECT: Assert before cast
assert isinstance(doc, MutableMapping), f"Expected MutableMapping, got {type(doc)}"
cast(dict[str, Any], doc)["key"] = value
```

`‍`When the cost of the assertion is trivial (O(1) checks like **isinstance**), always add it. Skip the assertion only when you have just performed a type guard, or in measured performance-critical hot paths with documented justification.

### 7. Use Literal Types for Fixed Values

When strings represent a fixed set of valid values, such as error codes, status values, or command types, model them in the type system using **Literal**. This catches typos at type-check time, enables IDE autocomplete, and documents valid values directly in the code.

```
from typing import Literal
from dataclasses import dataclass

# WRONG: Bare strings
issues.append(("orphen-state", "desc")) # Typo goes unnoticed!

# CORRECT: Literal type
IssueCode = Literal["orphan-state", "orphan-dir", "missing-branch"]

@dataclass(frozen=True)
class Issue:
 code: IssueCode
 message: str

issues.append(Issue(code="orphan-state", message="desc")) # Type-checked!
```

`‍`Before using a bare **str** type, ask: Is this string compared with **==** or **in** anywhere? Is there a fixed set of valid values? Would a typo cause a bug? If any answer is yes, use **Literal** instead.

### 8. Declare Variables Close to Use

Variables should be declared as close as possible to where they are used. Avoid early declarations that pollute scope and obscure data flow.

```
# WRONG: Variable declared 20 lines before use
def process_data(ctx, items):
 result_path = compute_result_path(ctx)
 # ... 20 lines of other logic ...
 save_to_path(transformed, result_path)

# CORRECT: Inline at call site
def process_data(ctx, items):
 # ... other logic ...
 save_to_path(transformed, compute_result_path(ctx))
```

`‍`This reduces cognitive load because readers do not need to scroll back to understand where a value came from. It also makes data flow visible at a glance. The exception is when a value is used multiple times or when inlining would hurt readability.

### 9. Keyword Arguments for Complex Functions

Functions with five or more parameters must use keyword-only arguments. Use the **\*** separator after the first positional parameter to enforce this at the language level.

```
# WRONG: Positional chaos - what do these values mean?
response = fetch_data(api_url, 30.0, 3, {"Accept": "application/json"}, token)

# CORRECT: Keyword-only after first param
def fetch_data(
 url,
 *,
 timeout: float,
 retries: int,
 headers: dict[str, str],
 auth_token: str,
) -> Response:
 ...

# Call site is self-documenting
response = fetch_data(
 api_url,
 timeout=30.0,
 retries=3,
 headers={"Accept": "application/json"},
 auth_token=token,
)
```

`‍`This improves call-site readability by forcing explicit parameter names. The first parameter (often **self**, **ctx**, or the primary subject of the function) can remain positional.

### 10. Default Values Are Dangerous

Avoid default parameter values unless absolutely necessary. They are a significant source of bugs because callers forget to pass a parameter and get unexpected results.

```
# DANGEROUS: Caller forgets encoding, gets wrong behavior
def process_file(path: Path, encoding: str = "utf-8") -> str:
 return path.read_text(encoding=encoding)

content = process_file(legacy_latin1_file) # Bug: should be encoding="latin-1"

# SAFER: Require explicit choice
def process_file(path: Path, encoding: str) -> str:
 return path.read_text(encoding=encoding)

content = process_file(legacy_latin1_file, encoding="latin-1")
```

`‍`When a default value is never overridden anywhere in your codebase, eliminate the parameter entirely or hardcode the value. Acceptable uses of defaults include truly optional behavior where the default is correct for 95%+ of callers, or temporary backwards compatibility when adding parameters to existing APIs.

## Build with Us

Want to copy and paste the full set of rules? You can find it [here](https://github.com/dagster-io/dagster-claude-plugins/blob/95a046e7955660ede6130954b740cd4623bc3a47/plugins/dignified-python/skills/dignified-python/dignified-python-core.md)! They reflect how we think about engineering, collaboration, and the craft of writing software that is both elegant and dependable. These are not abstract ideals. They shape how we work every day, and they make Dagster a place where engineers can do their best work with clarity, speed, and confidence.

And if you want to work on a product with real impact, in an environment that values its engineers and invests deeply in their workflows, we would love to meet you. [Apply and help us](https://dagster.io/company/careers) shape the future of data engineering.
