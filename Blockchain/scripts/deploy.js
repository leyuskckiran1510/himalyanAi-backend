const hre = require("hardhat");

async function main() {
  const UserStorage = await hre.ethers.getContractFactory("UserStorage");
  const userStorage = await UserStorage.deploy();
  await userStorage.waitForDeployment();
  
  const address = await userStorage.getAddress();
  console.log("UserStorage deployed to:", address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
  