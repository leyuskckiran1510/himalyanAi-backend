// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserStorage {
    struct UserData {
        string ipfsHash;
        uint256 timestamp;
    }
    
    mapping(address => UserData[]) public userHistory;
    
    event DataStored(address indexed user, string ipfsHash, uint256 timestamp);
    
    function storeUserData(string memory ipfsHash) public {
        UserData memory newData = UserData({
            ipfsHash: ipfsHash,
            timestamp: block.timestamp
        });
        
        userHistory[msg.sender].push(newData);
        emit DataStored(msg.sender, ipfsHash, block.timestamp);
    }
    
    function getUserHistory(address user) public view returns (UserData[] memory) {
        return userHistory[user];
    }
}
