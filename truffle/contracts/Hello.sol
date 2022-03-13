pragma solidity ^0.8.12;
contract Hello {
   string message;
   int counter;
   string proposal;

   constructor() {

   message = "Hello, World";
   proposal = "";
   counter = 0;

   }
   function getGreetings() public view returns (string memory)
   {
     return message;
   }
   function setGreetings(string memory _message) public{
     if (keccak256(abi.encodePacked(proposal)) == keccak256(abi.encodePacked(_message))) {
        counter += 1;
     } else {
        proposal = _message;
        counter = 1;
     }
     /// if counter >= f+1 commit the message
     if (counter >= 2) {
        message = proposal;
    }
   }

}
