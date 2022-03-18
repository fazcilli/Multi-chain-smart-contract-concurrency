const TPStorage = artifacts.require("TPStorage");

/*
 * uncomment accounts to access the test accounts made available by the
 * Ethereum client
 * See docs: https://www.trufflesuite.com/docs/truffle/testing/writing-tests-in-javascript
 */
contract("TPStorage", function (/* accounts */) {
  it("should assert true", async function () {
    await TPStorage.deployed();
    return assert.isTrue(true);
  });
});
