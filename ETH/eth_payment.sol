pragma solidity >=0.8.0;

contract Payment {
    struct Partner {
        address addr;
        uint256 balance;
    }

    struct Signature {
        uint8 v;
        bytes32 r;
        bytes32 s;
    }

    struct Man {
        string name;
        uint8 age;
    }

    Partner Bob =
        Partner(address(0xE78695495367b7e5a71913be5b31B200B371b58B), 100);
    Partner Ingrid =
        Partner(address(0xb5966F0B4272e91B77474da7212845D0759b2231), 100);

    mapping(address => bool) public partners;
    mapping(address => bool) public members_;

    uint256 sequence;
    uint256 fee;
    uint256 channelTime;
    uint256 waitRounds;
    uint256 delayTransfer;
    bool subOp2;

    mapping(address => bool) public members;

    event Log(bool result, uint256 balanceB, uint256 balanceI);

    constructor() public {
        subOp2 = false;
        channelTime = block.timestamp - 5 days;
        waitRounds = 10 hours;
        delayTransfer = 1 days;
        partners[Bob.addr] = true;
        partners[Ingrid.addr] = true;

        members[address(0x21694ba94A00E14DE6a362Bb069bE71d61cd1E12)] = true;
        members[address(0x114bcf97731B57713BDC4d029518287C6d49E1FD)] = true;
        members[address(0xA37bc56BE58FAA46351860c97c359a06365cA4f8)] = true;
        members[address(0x36541b93A01a9D4258e0387A3B96929ca34e4548)] = true;
        members[address(0xa10FefFF864e95Ac2720f2616D477F67061Cb7bD)] = true;
        sequence = 0;
        fee = 10;
    }

    function addrContains(address addr) public view returns (bool result) {
        result = members[addr];
    }

    function uploadMemSigs(Signature[] memory man)
        public
        payable
        returns (bool)
    {
        return false;
    }

    function subOperation2(
        uint256 balanceBob,
        uint256 balanceIngrid,
        bytes32 O_CVPCh,
        Signature memory signatureB,
        Signature memory signatureI,
        bytes32 TXh,
        Signature[] memory memSigs
    ) public payable returns (bool) {
        bool result = true;
        if (block.timestamp < channelTime) {
            return false;
        }

        address addrBob_ = ecr(
            O_CVPCh,
            signatureB.v,
            signatureB.r,
            signatureB.s
        );
        result = partners[addrBob_];

        address addrIngrid_ = ecr(
            O_CVPCh,
            signatureI.v,
            signatureI.r,
            signatureI.s
        );
        result = partners[addrIngrid_];

        if (result == false) {
            return false;
        }

        if ((block.timestamp - channelTime) < waitRounds) return false;

        address[] memory memAddr = new address[](5);
        uint256 count = 0;

        for (uint256 j = 0; j < 5; j++) {
            Signature memory memSig = memSigs[j];
            address addr_ = ecr(TXh, memSig.v, memSig.r, memSig.s);
            if (members_[addr_] == false && members[addr_] == true) {
                count = count + 1;
                members_[addr_] = true;
            }
        }

        if (count >= 3) {
            Ingrid.balance = balanceIngrid;
            Ingrid.balance += Ingrid.balance + fee;
            Bob.balance = balanceBob;
            fee = 0;
        } else {
            Bob.balance = Bob.balance + Ingrid.balance;
            Ingrid.balance = 0;
            fee = 0;
        }
        subOp2 = true;
        emit Log(result, Bob.balance, Ingrid.balance);

        return result;
    }

    function subOperation3(
        uint256 balanceBob,
        uint256 balanceIngrid,
        bytes32 O_CVPCh,
        Signature memory signatureB,
        Signature memory signatureI
    ) public payable returns (bool) {
        if (subOp2 == false) {
            return false;
        }

        if ((block.timestamp - channelTime) < delayTransfer) {
            return false;
        }

        address addrBob_ = ecr(
            O_CVPCh,
            signatureB.v,
            signatureB.r,
            signatureB.s
        );
        bool result = partners[addrBob_];

        if (result == false) {
            return false;
        }

        address addrIngrid_ = ecr(
            O_CVPCh,
            signatureI.v,
            signatureI.r,
            signatureI.s
        );
        result = partners[addrIngrid_];

        if (result == false) {
            return false;
        }

        Ingrid.balance = balanceIngrid;
        Bob.balance = balanceBob;

        emit Log(result, Bob.balance, Ingrid.balance);
        return true;
    }

    function ecr(
        bytes32 msgh,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public pure returns (address sender) {
        return ecrecover(msgh, v, r, s);
    }
}
