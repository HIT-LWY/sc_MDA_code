// SPDX-License-Identifier: GPL-3.0

pragma solidity >0.4.0;

contract License{

    //许可方
    address licensor_address;
    //被许可方
    address licensee_address;

    uint private constant signDate = 1591521413;
    uint private duration = 365;

    modifier check_licensor(){
        require(msg.sender == licensor_address);
        _;
    }

    modifier check_licensee(){
        require(msg.sender == licensee_address);
        _;
    }

    modifier validity(){
        require(signDate + duration * 1000 >= block.timestamp);
        _;
    }

    //许可方将某权利授予给某参与方
    uint private permissionRightStart;
    uint private permissionRightEnd;

    int private allPermissionPartyNum;
    mapping(int=>address) private allPermissionParty;

    //检查当前时间是否在规定的时间内
    modifier checkIfWithinTimePeriod(){
        require(block.timestamp >= permissionRightStart || block.timestamp <= permissionRightEnd,"Not in authorized time!");
        _;
    }
    //授权
    function oneAuthorizePermissionOther(address current_licensee) public check_licensor{
        allPermissionPartyNum++;
        allPermissionParty[allPermissionPartyNum] = current_licensee;
    }
    //判断某地址是否具有权限
    function ifPermissionAuthorization(address addr) public view checkIfWithinTimePeriod returns(bool){
        for(int i = 0; i < allPermissionPartyNum; i++){
            if(allPermissionParty[i] == addr){
                return true;
            }
        }
        return false;
    }
    //授权条款完成

    //初始权利设定与检查
    int private allMonitorRightNum = 1;
    mapping(int=>address) private allMonitorRight;

    constructor(address licensor, address licensee) public {
        licensor_address = licensor;
        licensee_address = licensee;
        allMonitorRight[1] = licensor;
    }

    //检查是否具有权限
    function ifMonitorAuthorization(address addr) public view returns(bool){
        for(int i = 0; i < allMonitorRightNum; i++){
            if(allMonitorRight[i] == addr){
                return true;
            }
        }
        return false;
    }
    //完成

    //一方向另一方提供物品
    int provideGoodsNum;
    struct provideGood{
        int goodId;
        uint time;
        string ipfsDocument;
    }
    mapping(int=>provideGood) allProvideGood;

    int receiveGoodsNum;
    struct receiveGood{
        int goodId;
        uint time;
    }
    mapping(int=>receiveGood) allReceiveGood;

    //被许可方向许可方提供样品
    function provideGoods(int sampleId, string memory document) public check_licensee{
        provideGoodsNum++;
        provideGood memory newProvideGood = provideGood(sampleId,block.timestamp,document);
        allProvideGood[provideGoodsNum] = newProvideGood;
    }

    //许可方确认接收物品
    function receiveGoods(int sampleId) public check_licensor{
        receiveGoodsNum++;
        receiveGood memory newReceiveGood = receiveGood(sampleId,block.timestamp);
        allReceiveGood[receiveGoodsNum] = newReceiveGood;
    }
    //完

    int private problemNum;
    struct problem{
        address sender;
        uint time;
        string problemDocument;
        bool ifExist;
        uint resolveTime;
        string resolveDocument;
    }
    mapping(int=>problem) private allProblems;

    uint private specSolveTime = 120 days;
    bool private licensorIfCanTerminate = false;

    //在某条件发生时，一方有权终止协议
    function sendProblemNotificationByLicensor(string memory document) public check_licensor validity returns(int){
        problemNum++;
        allProblems[provideGoodsNum] = problem(msg.sender,block.timestamp, document, false, 0,"");
        return problemNum;
    }
    function sendProblemNotificationByLicensee(string memory document) public check_licensee validity returns(int){
        problemNum++;
        allProblems[provideGoodsNum] = problem(msg.sender,block.timestamp, document, false, 0,"");
        return problemNum;
    }

    function resolveProblemByLicensee(int problemId,string memory document) public check_licensee validity{
        allProblems[problemId].resolveDocument = document;
        allProblems[problemId].ifExist = true;
        allProblems[problemId].resolveTime = block.timestamp;
    }
    function resolveProblemByLicensor(int problemId,string memory document) public check_licensor validity{
        allProblems[problemId].resolveDocument = document;
        allProblems[problemId].ifExist = true;
        allProblems[problemId].resolveTime = block.timestamp;
    }

    function checkSolveInSpecTimeByLicensor(int problemId) public check_licensor{
        require(allProblems[problemId].sender == msg.sender);
        uint start = allProblems[problemId].time;
        uint end = allProblems[problemId].resolveTime;
        if(allProblems[problemId].ifExist == true && start - end > specSolveTime){
            licensorIfCanTerminate = true;
        }
        else if (allProblems[problemId].ifExist == false && block.timestamp - start> specSolveTime){
            licensorIfCanTerminate = true;
        }
    }

    bool private licenseeIfCanTerminate = false;

    function checkSolveInSpecTimeByLicensee(int problemId) public check_licensee{
        require(allProblems[problemId].sender == msg.sender);
        uint start = allProblems[problemId].time;
        uint end = allProblems[problemId].resolveTime;
        if(allProblems[problemId].ifExist == true && start - end > specSolveTime){
            licenseeIfCanTerminate = true;
        }
        else if (allProblems[problemId].ifExist == false && block.timestamp - start> specSolveTime){
            licenseeIfCanTerminate = true;
        }
    }

    modifier checkIfLicensorIfCanTerminate(){
        require(licensorIfCanTerminate);
        _;
    }

    modifier checkIfLicenseeIfCanTerminate(){
        require(licenseeIfCanTerminate);
        _;
    }

    bool private ifContractIsValid = true;

    modifier checkContractIsValid(){
        require(ifContractIsValid);
        _;
    }

    function finishContractByLicensor() public check_licensor checkIfLicensorIfCanTerminate{
        ifContractIsValid = false;
    }

    function finishContractByLicensee() public check_licensee checkIfLicenseeIfCanTerminate{
        ifContractIsValid = false;
    }


    //完

    //归还物品
    int private needReturnGoodsNum = 0;
    struct needReturnGood{
        string information;
        uint appointReturnTime;
        bool ifReturn;
        uint realReturnTime;
        string returnDocument;
    }
    mapping(int=>needReturnGood) allNeedReturnGood;
    //设置需要归还的物品
    function setNeedReturnGood(string memory info, uint time) checkContractIsValid check_licensor public returns(int){
        needReturnGoodsNum++;
        allNeedReturnGood[needReturnGoodsNum] = needReturnGood(info,time,false,0,"");
        return needReturnGoodsNum;
    }
    //归还物品
    function returnGood(int id, string memory ipfs) public checkContractIsValid check_licensee {
        allNeedReturnGood[id].ifReturn = true;
        allNeedReturnGood[id].realReturnTime = block.timestamp;
        allNeedReturnGood[id].returnDocument = ipfs;
    }



}