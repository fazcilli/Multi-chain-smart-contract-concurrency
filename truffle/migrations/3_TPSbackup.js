const TPSbackup = artifacts.require("TPSbackup");

module.exports = function (deployer) {
  deployer.deploy(TPSbackup);
};