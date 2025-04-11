const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("UserStorage", function () {
    let UserStorage;
    let userStorage;
    let owner;
    let addr1;

    beforeEach(async function () {
        UserStorage = await ethers.getContractFactory("UserStorage");
        [owner, addr1] = await ethers.getSigners();
        userStorage = await UserStorage.deploy();
    });

    describe("Storing Data", function () {
        it("Should store IPFS hash", async function () {
            const ipfsHash = "QmTest123";
            await userStorage.storeUserData(ipfsHash);
            
            const history = await userStorage.getUserHistory(owner.address);
            expect(history[0].ipfsHash).to.equal(ipfsHash);
        });

        it("Should emit DataStored event", async function () {
            const ipfsHash = "QmTest123";
            
            await expect(userStorage.storeUserData(ipfsHash))
                .to.emit(userStorage, "DataStored")
                .withArgs(owner.address, ipfsHash, await ethers.provider.getBlock("latest").then(b => b.timestamp + 1));
        });

        it("Should store multiple entries for same user", async function () {
            await userStorage.storeUserData("QmHash1");
            await userStorage.storeUserData("QmHash2");
            
            const history = await userStorage.getUserHistory(owner.address);
            expect(history.length).to.equal(2);
            expect(history[0].ipfsHash).to.equal("QmHash1");
            expect(history[1].ipfsHash).to.equal("QmHash2");
        });
    });

    describe("Retrieving Data", function () {
        it("Should return empty array for new user", async function () {
            const history = await userStorage.getUserHistory(addr1.address);
            expect(history.length).to.equal(0);
        });
    });
});
