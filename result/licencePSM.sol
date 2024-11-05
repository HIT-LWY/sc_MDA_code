//TRADEMARK LICENSE AGREEMENT
pragma
contract License  {
    uint private specSolveTime = 120 days;
    bool private ifContractIsValid = true;
    uint private constant signDate = 1591521413;
    uint private duration = 365;
    int private needReturnGoodsNum = 0;
    mapping(int=>needReturnGood) private allNeedReturnGood ;
    struct needReturnGood{
    	string information;
    	uint appointReturnTime;
    	bool ifReturn;
    	uint realReturnTime;
    	string returnDocument;
    }
    bool private licenseeIfCanTerminate = false;
    bool private licensorIfCanTerminate = false;
    int private problemNum = 0;
    mapping(int=>problem) private allProblems ;
    struct problem{
    	address sender;
    	uint time;
    	string problemDocument;
    	bool ifExist;
    	uint resolveTime;
    	string resolveDocument;
    }
    int private provideGoodsNum = 0;
    struct provideGood{
    	int goodId;
    	uint time;
    	string ipfsDocument;
    }
    mapping(int=>provideGood) private allProvideGood ;
    int private receiveGoodsNum = 0;
    struct receiveGood{
    	int goodId;
    	uint time;
    }
    mapping(int=>receiveGood) private allReceiveGood ;
    address private licensor_address ;
    address private licensee_address ;
    int private allMonitorRightNum = 1;
    mapping(int=>address) private allMonitorRight ;
    uint private permissionRightStart = 0;
    uint private permissionRightEnd = 0;
    int private allPermissionPartyNum = 0;
    mapping(int=>address) private allPermissionParty ;
    address licensor;
    address licensee;
    
    modifier check_licensor(){
        require(msg.sender == licensor);
        _;
    }
    modifier check_licensee(){
        require(msg.sender == licensee);
        _;
    }
    modifier validity(){
        require(signDate + duration * 1000 >= block.timestamp);
        _;
    }
    modifier checkIfWithinTimePeriod(){
        require(block.timestamp >= permissionRightStart || block.timestamp <= permissionRightEnd,"Not in authorized time!");

        _;
        _;
    }
    modifier checkIfLicensorIfCanTerminate(){
        require(licensorIfCanTerminate);

        _;
        _;
    }
    modifier checkIfLicenseeIfCanTerminate(){
        require(licenseeIfCanTerminate);

        _;
        _;
    }
    modifier checkContractIsValid(){
        require(ifContractIsValid);

        _;
        _;
    }
    
    function set_licensor_address(address newAddr) public {
        require(msg.sender == licensor);
        licensor = newAddr;
    }
    function set_licensee_address(address newAddr) public {
        require(msg.sender == licensee);
        licensee = newAddr;
    }
    function oneAuthorizePermissionOther(address current_licensee) public  validity check_licensor {
        allPermissionPartyNum++;

        allPermissionParty[allPermissionPartyNum] = current_licensee;
    }
    function ifPermissionAuthorization(address addr) public  view checkIfWithinTimePeriod validity check_licensor returns (bool) {
        for(int i = 0; i < allPermissionPartyNum; i++){

        	if(allPermissionParty[i] == addr){

        		return true;

        	}

        }

        return false;
    }
    constructor(address licensor, address licensee){
        licensor_address = licensor;

        licensee_address = licensee;

        allMonitorRight[1] = licensor;
    }
    function ifMonitorAuthorization(address addr) public  view validity returns (bool) {
        for(int i = 0; i < allMonitorRightNum; i++){

        	if(allMonitorRight[i] == addr){

        		return true;

        	}

        }

        return false;
    }
    function provideGoods(int sampleId, string memory document) public  validity check_licensee {
        provideGoodsNum++;

        provideGood memory newProvideGood = provideGood(sampleId,block.timestamp,document);

        allProvideGood[provideGoodsNum] = newProvideGood;
    }
    function receiveGoods(int sampleId) public  validity check_licensor {
        receiveGoodsNum++;

        receiveGood memory newReceiveGood = receiveGood(sampleId,block.timestamp);

        allReceiveGood[receiveGoodsNum] = newReceiveGood;
    }
    function finishContractByLicensor() public  checkIfLicensorIfCanTerminate validity check_licensor {
        ifContractIsValid = false;
    }
    function finishContractByLicensee() public  checkIfLicenseeIfCanTerminate validity check_licensee {
        ifContractIsValid = false;
    }
    function sendProblemNotificationByLicensor(string memory document) public  validity check_licensor returns (int) {
        problemNum++;

        allProblems[provideGoodsNum] = problem(msg.sender,block.timestamp, document, false, 0,"");

        return problemNum;
    }
    function sendProblemNotificationByLicensee(string memory document) public  validity check_licensee returns (int) {
        problemNum++;

        allProblems[provideGoodsNum] = problem(msg.sender,block.timestamp, document, false, 0,"");

        return problemNum;
    }
    function resolveProblemByLicensee(int problemId, string memory document) public  validity check_licensee {
        allProblems[problemId].resolveDocument = document;

        allProblems[problemId].ifExist = true;

        allProblems[problemId].resolveTime = block.timestamp;
    }
    function resolveProblemByLicensor(int problemId, string memory document) public  validity check_licensor {
        allProblems[problemId].resolveDocument = document;

        allProblems[problemId].ifExist = true;

        allProblems[problemId].resolveTime = block.timestamp;
    }
    function setNeedReturnGood(string memory goodInformation, uint appointReturnTime) public  validity checkContractIsValid check_licensor returns (int) {
        needReturnGoodsNum++;

        allNeedReturnGood[needReturnGoodsNum] = needReturnGood(goodInformation,appointReturnTime,false,0,"");

        return needReturnGoodsNum;
    }
    
    
}