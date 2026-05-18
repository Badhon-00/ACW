# DEPEG Claude skill

Self-contained integration guide for Claude Code agents working with the [DEPEG protocol](https://depeg.app) — a Solana program that wraps pump.fun memecoins as 1:1 USDC-backed stablecoins with staking, boosters, and yield distribution.

The skill teaches an agent how to:

- Derive every public PDA (Config, StakingPool, StakePosition, UserPoolState, stablecoin mint / vault, ATAs).
- Decode the public on-chain account layouts.
- Build instructions for the user-facing surface (swap USDC ↔ stablecoin, stake, claim rewards, unstake, buy booster) and permissionless keeper ixs.
- Launch a new pool wrapping a pump.fun coin (`initialize_user_pool`, requires DEPEG admin co-signature).
- Parse the `DEPEG_PROTOCOL [depeg::*]` on-chain log format with decimal-formatted amounts (6 dp for USDC/stablecoin, 9 dp for SOL).

It pairs with the [`@depegprotocol/sdk`](https://www.npmjs.com/package/@depegprotocol/sdk) TypeScript package for code-level access.

## Install

```bash
git clone https://github.com/DepegOrg/claude-skill ~/.claude/skills/depeg
```

Then in any Claude Code session: `Skill: depeg` (or it loads automatically when the agent matches the description in `SKILL.md`).

## Updating

```bash
cd ~/.claude/skills/depeg && git pull
```

## License

MIT
