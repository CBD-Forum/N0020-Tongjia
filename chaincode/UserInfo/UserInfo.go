// ============================================================================================================================
// 本智能合约用于用户信息管理
// 功能包括：个人信息的增、删、改、查，信用积分的变更和查询，账户余额的变更和查询，兼职信息的添加
// ============================================================================================================================

package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/hyperledger/fabric/core/chaincode/shim"
	"strconv"
)

type SimpleChaincode struct {
}

// ============================================================================================================================
// UserInfo struct
// ============================================================================================================================
type UserInfoStruct struct {
	UserInfo    UserStaticInfoStruct
	CreditScore CreditScoreStruct
	Balance     string
	Jobs        []string
}

// ============================================================================================================================
// UserStaticInfo struct
// ============================================================================================================================
type UserStaticInfoStruct struct {
	UserID     string
	Gender     string
	School     string
	StuID      string
	Tele       string
	AgencyName string
	Role       string
	Username   string
	BCID       string
	Password   string
	RealName   string
	Status     string
}

// ============================================================================================================================
// CreditScore struct
// ============================================================================================================================
type CreditScoreStruct struct {
	CurrentCreditScore string
	TotalCreditScore   string
	Ratetimes          string
}

// ============================================================================================================================
// Init function
// ============================================================================================================================

func (t *SimpleChaincode) Init(stub shim.ChaincodeStubInterface, function string, args []string) ([]byte, error) {
	return nil, nil
}

// ============================================================================================================================
// Invoke function is the entry point for Invocations
// ============================================================================================================================
func (t *SimpleChaincode) Invoke(stub shim.ChaincodeStubInterface, function string, args []string) ([]byte, error) {

	// Handle different functions
	if function == "init" {
		return t.Init(stub, "init", args)
	} else if function == "add" { //add a new user
		return t.Add(stub, args)
	} else if function == "delete" { //deletes an user from its state
		return t.Delete(stub, args)
	} else if function == "edit" { //change the infor of the user
		return t.Edit(stub, args)
	} else if function == "creditScoreEdit" { // change the creditScore of the user
		return t.CreditScoreEdit(stub, args)
	} else if function == "addTX" { //add a new TX
		return t.AddTX(stub, args)
	} else if function == "autoSettle" {
		return t.AutoSettle(stub, args)
	}

	return nil, errors.New("Received unknown function invocation")
}

// ============================================================================================================================
// Add function is used for adding a new user
// 2 input
// "UserID","UserInfo"
// ============================================================================================================================
func (t *SimpleChaincode) Add(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	UserID := args[0]
	UserInfo := args[1]
	UserTest, _ := stub.GetState(UserID)

	//test if the user has been existed
	if UserTest != nil {
		return nil, errors.New("the user is existed")
	}

	// add the user
	err = stub.PutState(UserID, []byte(UserInfo))
	if err != nil {
		return nil, errors.New("Failed to add the user")
	}

	return nil, nil
}

// ============================================================================================================================
// Delete function is used for deleting a user
// 1 input
// "UserID"
// ============================================================================================================================
func (t *SimpleChaincode) Delete(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1. ")
	}
	UserID := args[0]
	UserInfo, err := stub.GetState(UserID)

	//test if the user has been existed
	if err != nil {
		return nil, errors.New("The user never been exited")
	}

	if UserInfo == nil {
		return nil, errors.New("The user`s information is empty!")
	}

	err = stub.DelState(UserID) //remove the key from chaincode state
	if err != nil {
		return nil, errors.New("Failed to delete the user. ")
	}

	return nil, nil
}

// ============================================================================================================================
// Edit function is used for changing the user's info
// 2 input
// "UserID","NewUserInfo"
// ============================================================================================================================
func (t *SimpleChaincode) Edit(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	UserID := args[0]
	NewUserInfo := args[1]
	OldUserInfo, err := stub.GetState(UserID)

	//test if the user has been existed
	if err != nil {
		return nil, errors.New("The user never been exited")
	}

	if OldUserInfo == nil {
		return nil, errors.New("The user`s information is empty!")
	}

	// edit the user
	err = stub.PutState(UserID, []byte(NewUserInfo))
	if err != nil {
		return nil, errors.New("Failed to edit the user")
	}

	return nil, nil
}

// ============================================================================================================================
// CreditScoreEdit function is used for change the account's credit score
// 2 input
// "UserID","NewScoreFromOthersNow"
// ============================================================================================================================
func (t *SimpleChaincode) CreditScoreEdit(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	UserID := args[0]
	NewScoreFromOthersNow, _ := strconv.Atoi(args[1])
	UserInfo, err := stub.GetState(UserID)

	//test if the user has been existed
	if err != nil {
		return nil, errors.New("The user never been exited")
	}
	if UserInfo == nil {
		return nil, errors.New("The user`s information is empty!")
	}

	var UserInfoJsonType UserInfoStruct //json type to accept the UserInfo from state

	err = json.Unmarshal(UserInfo, &UserInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	var TotalScore int
	var TotalTimes int
	var CurrentScore int

	TotalScore, _ = strconv.Atoi(string(UserInfoJsonType.CreditScore.TotalCreditScore))
	TotalTimes, _ = strconv.Atoi(string(UserInfoJsonType.CreditScore.Ratetimes))

	TotalScore += NewScoreFromOthersNow
	TotalTimes++
	CurrentScore = TotalScore / TotalTimes

	UserInfoJsonType.CreditScore.TotalCreditScore = strconv.Itoa(TotalScore)
	UserInfoJsonType.CreditScore.Ratetimes = strconv.Itoa(TotalTimes)
	UserInfoJsonType.CreditScore.CurrentCreditScore = strconv.Itoa(CurrentScore)

	// translate struct into json
	NewUserInfo, err := json.Marshal(UserInfoJsonType)
	if err != nil {
		return nil, err
	}
	// put the new score into state
	err = stub.PutState(UserID, NewUserInfo)
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// AddTX function is used to add TXID for the user
// 2 input
// "UserID","TXID"
// ============================================================================================================================
func (t *SimpleChaincode) AddTX(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	UserID := args[0]
	TXID := args[1]
	UserInfo, err := stub.GetState(UserID)

	//test if the user has been existed
	if err != nil {
		return nil, errors.New("The user never been exited")
	}
	if UserInfo == nil {
		return nil, errors.New("The user`s information is empty!")
	}

	var UserInfoJsonType UserInfoStruct //json type to accept the UserInfo from state

	err = json.Unmarshal(UserInfo, &UserInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	UserInfoJsonType.Jobs = append(UserInfoJsonType.Jobs, TXID)

	// translate struct into json
	NewUserInfo, err := json.Marshal(UserInfoJsonType)
	if err != nil {
		return nil, err
	}
	// put the new score into state
	err = stub.PutState(UserID, NewUserInfo)
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// AutoSettle function is used to change the balance of user
// 3 input
// "StuID","AgencyID","Salary"
// ============================================================================================================================
func (t *SimpleChaincode) AutoSettle(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 3 {
		return nil, errors.New("Incorrect number of arguments. Expecting 3. ")
	}
	StuID := args[0]
	AgencyID := args[1]
	Salary, _ := strconv.Atoi(args[2])
	StuInfo, err := stub.GetState(StuID)

	//test if the student has been existed
	if err != nil {
		return nil, errors.New("The student never been exited")
	}
	if StuInfo == nil {
		return nil, errors.New("The student`s information is empty!")
	}

	var UserInfoJsonTypeOfStu UserInfoStruct //json type to accept the UserInfo from state

	err = json.Unmarshal(StuInfo, &UserInfoJsonTypeOfStu)
	if err != nil {
		fmt.Println("error:", err)
	}

	OldBalanceOfStu, _ := strconv.Atoi(string(UserInfoJsonTypeOfStu.Balance))
	NewBalanceOfStu := OldBalanceOfStu + Salary
	UserInfoJsonTypeOfStu.Balance = strconv.Itoa(NewBalanceOfStu)

	// translate struct into json
	NewStuInfo, err := json.Marshal(UserInfoJsonTypeOfStu)
	if err != nil {
		return nil, err
	}
	// put the new score into state
	err = stub.PutState(StuID, NewStuInfo)
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	AgencyInfo, err := stub.GetState(AgencyID)

	//test if the agency has been existed
	if err != nil {
		return nil, errors.New("The agency never been exited")
	}
	if AgencyInfo == nil {
		return nil, errors.New("The agency`s information is empty!")
	}

	var UserInfoJsonTypeOfAgency UserInfoStruct //json type to accept the UserInfo from state

	err = json.Unmarshal(AgencyInfo, &UserInfoJsonTypeOfAgency)
	if err != nil {
		fmt.Println("error:", err)
	}

	OldBalanceOfAgency, _ := strconv.Atoi(string(UserInfoJsonTypeOfAgency.Balance))
	NewBalanceOfAgency := OldBalanceOfAgency - Salary
	UserInfoJsonTypeOfAgency.Balance = strconv.Itoa(NewBalanceOfAgency)

	// translate struct into json
	NewAgencyInfo, err := json.Marshal(UserInfoJsonTypeOfAgency)
	if err != nil {
		return nil, err
	}
	// put the new score into state
	err = stub.PutState(AgencyID, NewAgencyInfo)
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// Query function is the entry point for Queries
// ============================================================================================================================
func (t *SimpleChaincode) Query(stub shim.ChaincodeStubInterface, function string, args []string) ([]byte, error) {

	if function == "queryCurrentCreditScore" {
		return t.QueryCurrentCreditScore(stub, args)
	} else if function == "queryUserInfo" { // reply if the account is existed
		return t.QueryUserInfo(stub, args)
	}

	return nil, errors.New("No this function name, failed to query")

}

// ============================================================================================================================
// QueryCurrentCreditScore function is used to query the user`s current credit score.
// 1 input
// "UserID"
// ============================================================================================================================
func (t *SimpleChaincode) QueryCurrentCreditScore(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1 ")
	}
	UserID := args[0]
	UserInfo, err := stub.GetState(UserID)

	//test if the user has been existed
	if err != nil {
		return nil, errors.New("The user never been exited")
	}
	if UserInfo == nil {
		return nil, errors.New("The user`s information is empty!")
	}

	var UserInfoJsonType UserInfoStruct //json type to accept the UserInfo from state

	err = json.Unmarshal(UserInfo, &UserInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	return []byte(UserInfoJsonType.CreditScore.CurrentCreditScore), nil
}

// ============================================================================================================================
// QueryUserInfo function is used to return the whole information of the user.
// 1 input
// "UserID"
// ============================================================================================================================
func (t *SimpleChaincode) QueryUserInfo(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1 ")
	}
	UserID := args[0]

	// Get the state from the ledger
	UserInfo, err := stub.GetState(UserID)
	if err != nil {
		jsonResp := "{\"Error\":\"Failed to get state for " + UserID + "\"}"
		return nil, errors.New(jsonResp)
	}

	if UserInfo == nil {
		jsonResp := "{\"Error\":\"Nil content for " + UserID + "\"}"
		return nil, errors.New(jsonResp)
	}

	return UserInfo, nil
}

func main() {
	err := shim.Start(new(SimpleChaincode))
	if err != nil {
		fmt.Printf("Error starting Simple chaincode: %s", err)
	}
}
