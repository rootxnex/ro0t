# Cocokerel Web3 attestation layer

The Web3 layer is an optional integrity anchor for completed Cocokerel scans.
Scanning, findings, patches, GitHub credentials, policies, and reports remain
off-chain. The contract stores only fixed-width hashes, a verdict, timestamp,
and attester address.

## MVP network

- Test network: Base Sepolia (`chainId` 84532)
- Production network: not approved for the MVP
- No token, NFT, DAO, billing, or wallet-only authorization

## Attestation flow

1. The worker completes a scan and freezes its policy and report JSON.
2. Cocokerel serializes JSON canonically and computes SHA-256 hashes.
3. An authorized service wallet submits the four hashes and verdict.
4. The contract derives an immutable scan key and emits `ScanAttested`.
5. The dashboard compares the downloaded report hash with the on-chain value.

The service wallet must live in a managed signer or HSM. Never place its key in
the repository, frontend, database, or ordinary environment files.

## Privacy

`repositoryHash` is derived from the numeric GitHub repository ID, not its name.
This is pseudonymous rather than anonymous: anyone who knows the repository ID
can reproduce the hash. Private-repository teams must explicitly opt in.

## Contract behavior

- Only owner-authorized attesters can write.
- A repository/commit/policy tuple is immutable after its first attestation.
- Zero hashes and duplicate attestations revert.
- Ownership and attester changes emit auditable events.
- Reports can be verified without trusting the Cocokerel database.

Before Base mainnet use, add multisig ownership, managed signing, deployment
reproducibility, monitoring, and an independent contract audit.
