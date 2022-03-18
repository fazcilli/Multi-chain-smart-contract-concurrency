// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;

interface IStorage{
    function getQueueLastEntry() external view returns (string memory, uint);
}

// Sample struct to store basic key-value pair
struct info_piece { string key; uint value ;}

contract TPSbackup {
    address private TPSDuplicate;

    info_piece[] _storage;
    info_piece[] _queue;
    string temp;
    string backup_temp;

    function setBackupAddr(address ad) public{
        TPSDuplicate = ad;
    }

    function proposeValue(string memory k, uint val) public{
        EnqueueValue(k, val);
    }

    
    function EnqueueValue(string memory k, uint val) private{
        info_piece memory inf = info_piece(k, val);
        _queue.push(inf);
    }

    function DequeueValue() private view returns (string memory, uint){
        uint len = _queue.length;
        info_piece memory inf = _queue[len-1];
        return (inf.key, inf.value);
    }

    function store(string memory k, uint val) public{
        temp = k;
        info_piece memory inf = info_piece(k, val);
        if (crossCheckCommitValue()){
            _storage.push(inf);
        }
    }

    function getQueueLastEntry() public view returns (string memory, uint){
        return DequeueValue();
    }

    function crossCheckCommitValue() private returns (bool){
        uint val1; uint val2;
        (temp, val1) = DequeueValue();
        (backup_temp, val2) = getBackupQueueEntry();
        if ((keccak256(abi.encodePacked(temp)) == keccak256(abi.encodePacked(backup_temp))) && (val1 == val2)){
             return true;
        } else {
            revert("Different values sent to different contracts. Transaction cannot be validaed. ");
        }
    }

    function getLastStoredEntry() public view returns (string memory, uint){
        uint len = _storage.length;
        return (_storage[len-1].key, _storage[len-1].value);
    }

    function getBackupQueueEntry() private view returns (string memory, uint){
        return IStorage(TPSDuplicate).getQueueLastEntry();
    }
}