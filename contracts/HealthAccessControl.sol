// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract HealthAccessControl {
    address public admin;
    enum Role { NONE, PATIENT, DOCTOR, NURSE, INSURER, DEVICE }

    struct Record { address owner; string pointer; bool exists; }
    struct AccessGrant { bool allowed; uint256 expiresAt; }

    mapping(bytes32 => Record) public records;
    mapping(bytes32 => mapping(address => AccessGrant)) public grants;
    mapping(address => Role) public roles;

    event RecordRegistered(bytes32 indexed recordId, address indexed owner, string pointer);
    event GrantCreated(bytes32 indexed recordId, address indexed grantee, uint256 expiresAt);
    event AccessGranted(bytes32 indexed recordId, address indexed requester);
    event UnauthorizedAccessAttempt(bytes32 indexed recordId, address indexed requester);

    constructor() { admin = msg.sender; }

    function registerRecord(bytes32 recordId, address owner, string calldata pointer) external {
        require(!records[recordId].exists, "record exists");
        records[recordId] = Record(owner, pointer, true);
        emit RecordRegistered(recordId, owner, pointer);
    }

    function grantAccess(bytes32 recordId, address grantee, uint256 expiresAt) external {
        require(records[recordId].exists, "no record");
        require(msg.sender == records[recordId].owner || msg.sender == admin, "not owner/admin");
        grants[recordId][grantee] = AccessGrant(true, expiresAt);
        emit GrantCreated(recordId, grantee, expiresAt);
    }

    function requestAccess(bytes32 recordId) external {
        AccessGrant memory g = grants[recordId][msg.sender];
        if (g.allowed && (g.expiresAt == 0 || block.timestamp <= g.expiresAt)) {
            emit AccessGranted(recordId, msg.sender);
        } else {
            emit UnauthorizedAccessAttempt(recordId, msg.sender);
        }
    }

    function getPointer(bytes32 recordId) external view returns (string memory) {
        return records[recordId].pointer;
    }
}
