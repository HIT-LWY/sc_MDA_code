//TRADEMARK LICENSE AGREEMENT
contract License  {
    struct permissionRight{
    	bool hasRight;
    	bool isTransferable;
    }
    map private allPermissionParty ;
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