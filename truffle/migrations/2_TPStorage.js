const TPS = artifacts.require("TPStorage");

module.exports = function (deployer) {
  deployer.deploy(TPS);
};