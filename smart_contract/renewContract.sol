// SPDX-License-Identifier: GPL-3.0

pragma solidity >0.4.0;

contract renewContract {

    uint256 ifNotice = 0;
    uint256 constant autoRenewTime = 356 days;
    uint256 constant advanceNoticeTime = 30 days;
    uint256 ifAgreeRenew = 0;
    uint256 ifAgreeFinish = 0;
    uint256 constant needAgreeRenewNum = 2;
    uint256 constant needAgreeFinishNum = 1;

    address landlord;
    address tenant;

    //时间戳，2020-06-07 17:16:53，经过的秒数
    uint256 constant signDate = 1591521413;
    //单位是秒
    uint256 duration = 365 days;


    function set_landlord_address(address newAddr) public {
        require(msg.sender == landlord);
        landlord = newAddr;
    }

    //自动生成
    modifier check_landlord(){
        require(msg.sender == landlord);
        _;
    }
    modifier check_tenant(){
        require(msg.sender == tenant);
        _;
    }
    modifier check_landlord_tenant(){
        require(msg.sender == tenant || msg.sender == landlord);
        _;
    }

    //需要匹配,检查通知
    modifier checkNotice(){
        require(ifNotice != 0);  
        _;
    }
    modifier checkNoNotice(){
        require(ifNotice == 0);  
        _;
    }
    modifier checkNoticeTime(){
        require(signDate + duration * 1000 - advanceNoticeTime * 1000 >= block.timestamp);
        _;
    }

    //需要匹配有效期
    modifier validity(){
        require(signDate + duration * 1000 >= block.timestamp);
        _;
    }


    //需要一个变量来记录有多个参与方
    modifier checkIfAgreeRenew(){
        require(ifAgreeRenew >= needAgreeRenewNum);
        _;
    }
    modifier checkIfAgreeFinish(){
        require(ifAgreeFinish >= needAgreeFinishNum);
        _;
    }

    //输入sendMessage ,public, check_landlord_tenant
    //ifNotice是数据，需要占位
    function sendMessage() public check_landlord_tenant checkNoticeTime validity{
        ifNotice = 1;
    }

    //匹配 自动续约
    function autoRenew() public checkNoNotice check_landlord_tenant {
        duration += autoRenewTime;
    }

    //双方同意续约
    function agreeRenew() public check_landlord_tenant checkNotice validity{
        ifAgreeRenew++;
    }

    //双方同意结束合约
    function agreeFinish() public check_landlord_tenant checkNotice validity{
        ifAgreeFinish++;
    }

    //手动续约，前提是双方同意
    function renewByConsult(uint256 renewalTime) public checkIfAgreeRenew check_landlord {
        duration += renewalTime;
    }

    //结束合约
    function finishContract() public check_landlord  checkIfAgreeFinish {
        selfdestruct(msg.sender);
    }

    event a(int x);

}