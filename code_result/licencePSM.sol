//TRADEMARK LICENSE AGREEMENT
contract License  {
    struct permissionRight{
    	bool hasRight;
    	bool isTransferable;
    }
    mapping(address=>permissionRight) private allPermissionParty;
    uint private constant contractStart = 1343750400;
    uint private contractEnd = 1438358400;
    address licensor;
    function set_licensor_address(address newAddr) public {
        require(msg.sender == licensor);
        licensor = newAddr;
    }
    modifier check_licensor(){
        require(msg.sender == licensor);
        _;
    }
    address licensee;
    function set_licensee_address(address newAddr) public {
        require(msg.sender == licensee);
        licensee = newAddr;
    }
    modifier check_licensee(){
        require(msg.sender == licensee);
        _;
    }
    
    //Check if it is within the specified time period
    modifier checkIfWithinTimePeriod() {
        require(block.timestamp >= contractStart && block.timestamp <= contractEnd,"Not in authorized time!");
    	_;
    }
    
    
    // Granting a permission right
    function oneAuthorizePermissionOther(address addr) public check_licensor {
        allPermissionParty[addr].hasRight = true;
    }
    // Determine if permission is granted
    function ifPermissionAuthorization(address addr) public view checkIfWithinTimePeriod check_licensor returns (bool){
        return allPermissionParty[addr].hasRight;
    }
    
}