//TRADEMARK LICENSE AGREEMENT
contract License  {
    int private allPermissionPartyNum = 0;
    mapping(int=>address) private allPermissionParty ;
    uint private permissionRightStart = 0;
    uint private permissionRightEnd = 0;
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
    
    
    
    
}