// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Cocokerel scan attestations
/// @notice Stores hashes and verdicts only. Reports, source, and findings remain off-chain.
contract CocokerelAttestations {
    enum Verdict {
        Safe,
        ReviewRequired,
        Block
    }

    struct Attestation {
        bytes32 repositoryHash;
        bytes32 commitHash;
        bytes32 policyHash;
        bytes32 reportHash;
        Verdict verdict;
        uint64 recordedAt;
        address attester;
        bool exists;
    }

    address public owner;
    mapping(address => bool) public authorizedAttesters;
    mapping(bytes32 => Attestation) private attestations;

    error Unauthorized();
    error InvalidValue();
    error AlreadyAttested();

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event AttesterAuthorizationChanged(address indexed attester, bool authorized);
    event ScanAttested(
        bytes32 indexed scanKey,
        bytes32 indexed repositoryHash,
        bytes32 indexed commitHash,
        bytes32 policyHash,
        bytes32 reportHash,
        Verdict verdict,
        address attester
    );

    constructor(address initialOwner) {
        if (initialOwner == address(0)) revert InvalidValue();
        owner = initialOwner;
        authorizedAttesters[initialOwner] = true;
        emit OwnershipTransferred(address(0), initialOwner);
        emit AttesterAuthorizationChanged(initialOwner, true);
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized();
        _;
    }

    modifier onlyAttester() {
        if (!authorizedAttesters[msg.sender]) revert Unauthorized();
        _;
    }

    function setAttester(address attester, bool authorized) external onlyOwner {
        if (attester == address(0)) revert InvalidValue();
        authorizedAttesters[attester] = authorized;
        emit AttesterAuthorizationChanged(attester, authorized);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        if (newOwner == address(0)) revert InvalidValue();
        address previousOwner = owner;
        owner = newOwner;
        emit OwnershipTransferred(previousOwner, newOwner);
    }

    function scanKey(bytes32 repositoryHash, bytes32 commitHash, bytes32 policyHash)
        public
        pure
        returns (bytes32)
    {
        return keccak256(abi.encode(repositoryHash, commitHash, policyHash));
    }

    function attest(
        bytes32 repositoryHash,
        bytes32 commitHash,
        bytes32 policyHash,
        bytes32 reportHash,
        Verdict verdict
    ) external onlyAttester returns (bytes32 key) {
        if (
            repositoryHash == bytes32(0) || commitHash == bytes32(0)
                || policyHash == bytes32(0) || reportHash == bytes32(0)
        ) revert InvalidValue();
        key = scanKey(repositoryHash, commitHash, policyHash);
        if (attestations[key].exists) revert AlreadyAttested();
        attestations[key] = Attestation({
            repositoryHash: repositoryHash,
            commitHash: commitHash,
            policyHash: policyHash,
            reportHash: reportHash,
            verdict: verdict,
            recordedAt: uint64(block.timestamp),
            attester: msg.sender,
            exists: true
        });
        emit ScanAttested(
            key, repositoryHash, commitHash, policyHash, reportHash, verdict, msg.sender
        );
    }

    function getAttestation(bytes32 key) external view returns (Attestation memory) {
        return attestations[key];
    }
}
