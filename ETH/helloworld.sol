// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
import "./committee1.sol";
contract Greeter {
    uint _number;
    uint _amount_a;
    uint _amount_b;
    bytes  _sign_b;
    uint _time;//Operation effective time
    uint a_time;//Block current time
    uint public temperature;
    address account2_publickey;
    address account3_publickey;
    address payable account2;
    address payable account3;
    uint time_cvc_validity; //Virtual channel validity time
    uint time_cvc_expire;
    uint _number_nClose;
    uint _amount_a_nClose;
    uint _amount_b_nClose;

        //  Return contract address
         function getThis() view  public returns(address){
             return address(this);
         }
        //  Transfer money to contract address
         function pay() payable public{          
        }
        // Get the contract address balance
        function getBalance() view public returns(uint){
            return address(this).balance;
        }
        // Get the balance of an address
        function getBalance1(address account) view public returns(uint){
            return account.balance;
        }
        function svalue(address payable addr,uint amount) public payable returns(address) {
        //Enter the address and transfer 2 Ether coins to the corresponding address. The unit here is Gwei.
            addr.transfer(amount);
            return msg.sender;
        }
        // Get current time
        function get_time() view public returns(uint){
            return block.timestamp;
        }
        function update_time()  public returns(uint){
            _time=50;
            return _time;
        }
        function getTime() public view returns(uint){
            return _time;
        }
        function saveAccount_publickey(address _account2_publickey,address  _account3_publickey) public {
            account2_publickey=_account2_publickey;
            account3_publickey=_account3_publickey;
        }
        function saveAccount(address payable _account2,address payable _account3) public {
            account2=_account2;
            account3=_account3;
        }
        // Submit transaction information a
        function submit_transaction_a(uint number,uint amount_a,uint amount_b,bytes32 hash,uint8 v,bytes32 r,bytes32 s,uint time) payable public returns(bool) {
            _number = number;
            _amount_a=amount_a;
            _amount_b=amount_b;
            _time=time;
            a_time=block.timestamp;
            // There is another step of verification here
            address sign_publicKey;
            sign_publicKey=decode(hash,v,r,s);
            require(sign_publicKey==account3_publickey);
            return true;
        }
        // Submit transaction information b
        function submit_transaction_b(uint number,uint amount_a,uint amount_b,bytes32 hash,uint8 v,bytes32 r,bytes32 s,address payable addr,address payable addr2) payable public returns(bool){
            // Verification
            address sign_publicKey;
            sign_publicKey=decode(hash,v,r,s);
            if(sign_publicKey==account2_publickey)
            {
                if(block.timestamp<=(a_time+_time * 1 minutes)){
                   if(_number==number){
                      addr.transfer(amount_a);
                      addr2.transfer(amount_b);
                      
                    }
                    else if(_number<number){
                      addr.transfer(amount_a);
                      addr2.transfer(amount_b);
                      
                    }
                else{
                    addr.transfer(_amount_a);
                    addr2.transfer(_amount_b);
                    }
                }
                return true;
            }
            else
            {
                return false;
            }
        }
        function check_cvc_Validity(bytes32 hash_a,uint8 v_a,bytes32 r_a,bytes32 s_a) public view returns(bool){
            address sign_publickey_Ingrid;
            sign_publickey_Ingrid = decode(hash_a,v_a,r_a,s_a);
            if(sign_publickey_Ingrid==account2_publickey){
                if(block.timestamp>=time_cvc_expire){
                    return true;
                }
                else{
                    return false;
                }
            }
            else{
                return false;
            }
        }
        function close_cvc_abnormal(bytes32 hash_a,uint8 v_a,bytes32 r_a,bytes32 s_a,bytes32 hash,uint8 v,bytes32 r,bytes32 s) public view returns(bool){
            address sign_publicKey_a;
            sign_publicKey_a=decode(hash_a,v_a,r_a,s_a);
            require(sign_publicKey_a==account3_publickey);
            address sign_publicKey_b;
            sign_publicKey_b=decode(hash,v,r,s);
            require(sign_publicKey_b==account2_publickey);
            return true;
        }
        function close_cvc_abnormal_1(address _committeeAddress, uint _transactionId,uint Ingrid_and_Bob_Balance, uint zero) public returns (bool){
            committee _committee = committee(_committeeAddress);
            uint res ;
            res = _committee.getTrue(_transactionId);
            if (res==1){
                account2.transfer(Ingrid_and_Bob_Balance);
                account3.transfer(zero);
            }
            else{
                account2.transfer(zero);
                account3.transfer(Ingrid_and_Bob_Balance);
            }
           return true;
        }
        
        // Verification
        //Signature verification data entry function
        // bytes32 hash, bytes memory signedString
        function decode(bytes32 msgh,uint8 v,bytes32 r,bytes32 s) public pure returns(address){
            return ecrecover(msgh,v,r,s);
        }
        //Cut the original data into segments to specified lengths
       function slice(bytes memory data, uint start, uint len) pure public returns (bytes memory){
            bytes memory b = new bytes(len);
            for(uint i = 0; i < len; i++){
               b[i] = data[i + start];
            }
            return b;
        }
        //Use ecrecover to recover the public key
        function ecrecoverDecode(bytes32 r, bytes32 s, bytes1 v1) pure public returns (address addr){
            uint8 v = uint8(v1) + 27;
            addr = ecrecover(hex"4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45", v, r, s);
        }
        //Convert bytes to bytes32
        function bytesToBytes32(bytes memory source) pure public returns (bytes32 result) {
            assembly {
                result := mload(add(source, 32))
            }
        }
}