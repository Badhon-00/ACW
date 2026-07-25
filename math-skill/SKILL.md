---
name: math-skill
description: Comprehensive mathematical reasoning for AI agents — from arithmetic to research-level problems with rigorous step-by-step derivation, multi-method verification, and transparent uncertainty handling.
---

# Math.skill

This skill equips AI agents with a disciplined mathematical workflow: every problem is parsed, modeled, solved with full justifications, verified through multiple independent checks, and only then delivered as a final answer. Covers 30+ mathematical domains from basic arithmetic to abstract algebra and real analysis.

## When to Use This Skill

- Solving equations, systems, inequalities, or optimization problems
- Performing calculus operations (limits, derivatives, integrals, series)
- Working with linear algebra (matrices, eigenvalues, vector spaces)
- Writing or verifying mathematical proofs
- Analyzing functions, sequences, or probability distributions
- Checking the correctness of an existing mathematical solution
- Generating well-posed math problems with verified solutions
- Handling competition-level or research-level mathematical questions

## What This Skill Does

1. **Classifies the Problem**: Categorizes input into one of 34 mathematical domains to select the appropriate reasoning strategy and verification methods
2. **Parses Conditions Explicitly**: Extracts given conditions, goals, variable domains, implicit constraints, and special properties (symmetry, parity, convexity)
3. **Applies Rigorous Step-by-Step Reasoning**: Executes the chosen method with complete mathematical justification — every algebraic manipulation, theorem citation, and intermediate result clearly stated
4. **Verifies Through Multiple Independent Methods**: Applies at least two verification methods (back-substitution, domain check, numerical sampling, reverse derivation, independent cross-validation, etc.)
5. **Handles Errors Transparently**: Detects and corrects errors through backtracking, and qualifies uncertainty honestly when a solution cannot be fully verified
6. **Adapts Output to User Needs**: Supports multiple output modes — standard derivation, answer-only, proof format, solution checking, higher mathematics, and research-level reporting

## How to Use

### Basic Usage

Ask any mathematical question — the skill activates automatically when math is detected:

```
Solve x^2 - 5x + 6 = 0
```

```
Find the derivative of f(x) = e^x * sin(x)
```

```
Prove that sqrt(2) is irrational
```

### Advanced Usage

Request specific output formats or verification depth:

```
Explain the Fourier series of a square wave step by step, with verification
```

```
Check if this solution is correct: the integral of 1/x from -1 to 1 is 0
```

```
Generate a challenging combinatorics problem for an undergraduate exam, with solution
```

## Example

**User**: "Find all real solutions to x^3 - 3x^2 + 4 = 0"

**Output**:

> **Problem Analysis**: Cubic equation, real roots. Domain: all real numbers.
>
> **Method**: Rational root test → factor theorem → solve remaining quadratic.
>
> **Solution**:
> 1. Test possible rational roots (±1, ±2, ±4): x = 2 gives 8 - 12 + 4 = 0 ✓
> 2. Factor out (x - 2): (x - 2)(x^2 - x - 2) = 0
> 3. Solve quadratic: x^2 - x - 2 = (x - 2)(x + 1) = 0 → x = 2, x = -1
> 4. So (x - 2)^2(x + 1) = 0
>
> **Verification**:
> - Back-substitution: x = 2 → 8 - 12 + 4 = 0 ✓; x = -1 → -1 - 3 + 4 = 0 ✓
> - Domain check: no division, no radicals — all real numbers valid ✓
>
> **Final Answer**: x = 2 (multiplicity 2), x = -1

**Inspired by:** Structured mathematical reasoning workflows used in competition mathematics and academic tutoring

## Tips

- For best results, state the problem clearly with all conditions (domain, variable types)
- If you want a specific output format, mention it explicitly (e.g., "proof", "answer only")
- The skill can detect and correct its own errors — if verification fails, it backtracks automatically
- Install via `npx skills add Wholiver/Math.Skill`
- The full skill includes 9 supporting module files (11,007+ lines total) covering classification, verification, error prevention, and domain-specific protocols

## Common Use Cases

- Homework and exam problem solving
- Mathematical proof construction and verification
- Data analysis involving statistical computations
- Engineering and physics calculations
- Teaching and tutoring with detailed step-by-step explanations
- Code review for numerical algorithms
- Competition math training
