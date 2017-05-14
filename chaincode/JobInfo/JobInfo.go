// ============================================================================================================================
// 本智能合约用于兼职信息管理
// 功能包括：兼职信息的增、删、改、查，统计数据的更新，订单信息的添加
// ============================================================================================================================

package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/hyperledger/fabric/core/chaincode/shim"
	"github.com/hyperledger/fabric/core/util"
	"strconv"
)

type SimpleChaincode struct {
}

// ============================================================================================================================
// JobInfo struct
// ============================================================================================================================
type JobInfoStruct struct {
	JobID          string
	UserID         string
	AgencyName     string
	JobDetail      JobStaticInfoStruct
	Txs            []string
	TotalApplied   string
	TotalWaitCheck string
	TotalHired     string
	TotalSettled   string
}

// ============================================================================================================================
// UserStaticInfo struct
// ============================================================================================================================
type JobStaticInfoStruct struct {
	JobTime string
	Place   string
	Salary  string
	Day     string
	Demand  string
	Title   string
}

const UserInfoChaincodeID string = "9d29747f0b642ed65f481fbc1132d518834b3099671ad5d86feb8609202197f26cefcca348942ce9facdbe8312b5d7ee5598a6d9522c34ae9755720c1176a598"

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
	} else if function == "add" { //add a new job
		return t.Add(stub, args)
	} else if function == "delete" { //deletes an job from its state
		return t.Delete(stub, args)
	} else if function == "edit" { //change the infor of the job
		return t.Edit(stub, args)
	} else if function == "addTX" { //add a new TX
		return t.AddTX(stub, args)
	} else if function == "addTotalApplied" { //add 1 when a student applied the job
		return t.AddTotalApplied(stub, args)
	} else if function == "addTotalWaitCheck" { //add 1 when auto check not passed
		return t.AddTotalWaitCheck(stub, args)
	} else if function == "addTotalHired" { //add 1 when auto check passed or agency check passed
		return t.AddTotalHired(stub, args)
	} else if function == "addTotalSettled" { //add 1 when auto settle passed or agency settle passed
		return t.AddTotalSettled(stub, args)
	}

	return nil, errors.New("Received unknown function invocation")
}

// ============================================================================================================================
// Add function is used for adding a new job
// 2 input
// "JobID","JobInfo"
// ============================================================================================================================
func (t *SimpleChaincode) Add(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	JobID := args[0]
	JobInfo := args[1]
	JobTest, _ := stub.GetState(JobID)

	//test if the job has been existed
	if JobTest != nil {
		return nil, errors.New("the user is existed")
	}

	// add the job
	err = stub.PutState(JobID, []byte(JobInfo))
	if err != nil {
		return nil, errors.New("Failed to add the job")
	}

	var JobInfoJsonType JobInfoStruct //json type to accept the JobInfo from state
	err = json.Unmarshal([]byte(JobInfo), &JobInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	//invoke UserInfo chaincode to add this job`s ID attach to the agency who publish this job
	f := "addTX"
	invokeArgs := util.ToChaincodeArgs(f, JobInfoJsonType.UserID, JobInfoJsonType.JobID)
	response, err := stub.InvokeChaincode(UserInfoChaincodeID, invokeArgs)
	if err != nil {
		errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
		fmt.Printf(errStr)
		return nil, errors.New(errStr)
	}
	fmt.Printf("Invoke chaincode successful. Got response %s", string(response))

	return nil, nil
}

// ============================================================================================================================
// Delete function is used for deleting a job
// 1 input
// "JobID"
// ============================================================================================================================
func (t *SimpleChaincode) Delete(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1. ")
	}
	JobID := args[0]
	JobInfo, err := stub.GetState(JobID)

	//test if the job has been existed
	if err != nil {
		return nil, errors.New("The job never been exited")
	}

	if JobInfo == nil {
		return nil, errors.New("The job`s information is empty!")
	}

	err = stub.DelState(JobID) //remove the key from chaincode state
	if err != nil {
		return nil, errors.New("Failed to delete this job information! ")
	}

	return nil, nil
}

// ============================================================================================================================
// Edit function is used for changing the job's info
// 2 input
// "JobID","NewJobInfo"
// ============================================================================================================================
func (t *SimpleChaincode) Edit(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	JobID := args[0]
	NewJobInfo := args[1]
	OldJobInfo, err := stub.GetState(JobID)

	//test if the job has been existed
	if err != nil {
		return nil, errors.New("The job never been exited")
	}

	if OldJobInfo == nil {
		return nil, errors.New("The job`s information is empty!")
	}

	// edit the job
	err = stub.PutState(JobID, []byte(NewJobInfo))
	if err != nil {
		return nil, errors.New("Failed to edit the job")
	}

	return nil, nil
}

// ============================================================================================================================
// AddTotalApplied function is used to add 1 when a student applied the job
// 1 input
// "JobID"
// ============================================================================================================================
func (t *SimpleChaincode) AddTotalApplied(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1. ")
	}
	JobID := args[0]
	JobInfo, err := stub.GetState(JobID)

	//test if the job has been existed
	if err != nil {
		return nil, errors.New("The job never been exited")
	}
	if JobInfo == nil {
		return nil, errors.New("The job`s information is empty!")
	}

	var JobInfoJsonType JobInfoStruct //json type to accept the JobInfo from state

	err = json.Unmarshal(JobInfo, &JobInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	var TotalAppliedValue int
	TotalAppliedValue, _ = strconv.Atoi(string(JobInfoJsonType.TotalApplied))
	TotalAppliedValue++
	JobInfoJsonType.TotalApplied = strconv.Itoa(TotalAppliedValue)

	// put the new score into state
	a, err := json.Marshal(JobInfoJsonType)
	if err != nil {
		return nil, err
	}
	err = stub.PutState(JobID, []byte(a))
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// AddTotalWaitCheck function is used to add 1 when auto check not passed
// 1 input
// "JobID","1/-1"
// ============================================================================================================================
func (t *SimpleChaincode) AddTotalWaitCheck(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	JobID := args[0]
	Num, _ := strconv.Atoi(args[1])
	JobInfo, err := stub.GetState(JobID)

	//test if the job has been existed
	if err != nil {
		return nil, errors.New("The job never been exited")
	}
	if JobInfo == nil {
		return nil, errors.New("The job`s information is empty!")
	}

	var JobInfoJsonType JobInfoStruct //json type to accept the JobInfo from state

	err = json.Unmarshal(JobInfo, &JobInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	var TotalWaitCheckValue int
	TotalWaitCheckValue, _ = strconv.Atoi(string(JobInfoJsonType.TotalWaitCheck))
	TotalWaitCheckValue += Num
	JobInfoJsonType.TotalWaitCheck = strconv.Itoa(TotalWaitCheckValue)

	// put the new score into state
	a, err := json.Marshal(JobInfoJsonType)
	if err != nil {
		return nil, err
	}
	err = stub.PutState(JobID, []byte(a))
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// AddTotalHired function is used to add 1 when auto check passed or agency check passed
// 1 input
// "JobID"
// ============================================================================================================================
func (t *SimpleChaincode) AddTotalHired(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1. ")
	}
	JobID := args[0]
	JobInfo, err := stub.GetState(JobID)

	//test if the job has been existed
	if err != nil {
		return nil, errors.New("The job never been exited")
	}
	if JobInfo == nil {
		return nil, errors.New("The job`s information is empty!")
	}

	var JobInfoJsonType JobInfoStruct //json type to accept the JobInfo from state

	err = json.Unmarshal(JobInfo, &JobInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	var TotalHiredValue int
	TotalHiredValue, _ = strconv.Atoi(string(JobInfoJsonType.TotalHired))
	TotalHiredValue++
	JobInfoJsonType.TotalHired = strconv.Itoa(TotalHiredValue)

	// put the new score into state
	a, err := json.Marshal(JobInfoJsonType)
	if err != nil {
		return nil, err
	}
	err = stub.PutState(JobID, []byte(a))
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// AddTotalSettled function is used to add 1 when auto settle passed or agency settle passed
// 1 input
// "JobID"
// ============================================================================================================================
func (t *SimpleChaincode) AddTotalSettled(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1. ")
	}
	JobID := args[0]
	JobInfo, err := stub.GetState(JobID)

	//test if the job has been existed
	if err != nil {
		return nil, errors.New("The job never been exited")
	}
	if JobInfo == nil {
		return nil, errors.New("The job`s information is empty!")
	}

	var JobInfoJsonType JobInfoStruct //json type to accept the JobInfo from state

	err = json.Unmarshal(JobInfo, &JobInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	var TotalSettledValue int
	TotalSettledValue, _ = strconv.Atoi(string(JobInfoJsonType.TotalSettled))
	TotalSettledValue++
	JobInfoJsonType.TotalSettled = strconv.Itoa(TotalSettledValue)

	// put the new score into state
	a, err := json.Marshal(JobInfoJsonType)
	if err != nil {
		return nil, err
	}
	err = stub.PutState(JobID, []byte(a))
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// AddTX function is used to add TXID for the job
// 1 input
// "JobID","TXID"
// ============================================================================================================================
func (t *SimpleChaincode) AddTX(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	JobID := args[0]
	TXID := args[1]
	JobInfo, err := stub.GetState(JobID)

	//test if the job has been existed
	if err != nil {
		return nil, errors.New("The job never been exited")
	}
	if JobInfo == nil {
		return nil, errors.New("The job`s information is empty!")
	}

	var JobInfoJsonType JobInfoStruct //json type to accept the JobInfo from state

	err = json.Unmarshal(JobInfo, &JobInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	JobInfoJsonType.Txs = append(JobInfoJsonType.Txs, TXID)

	// put the new info into state
	a, err := json.Marshal(JobInfoJsonType)
	if err != nil {
		return nil, err
	}
	err = stub.PutState(JobID, []byte(a))
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// Query function is the entry point for Queries
// ============================================================================================================================
func (t *SimpleChaincode) Query(stub shim.ChaincodeStubInterface, function string, args []string) ([]byte, error) {

	if function == "queryJobInfo" {
		return t.QueryJobInfo(stub, args)
	} else if function == "queryAgencyID" {
		return t.QueryAgencyID(stub, args)
	} else if function == "querySalary" {
		return t.QuerySalary(stub, args)
	}

	return nil, errors.New("failed to query")

}

// ============================================================================================================================
// QueryJobInfo function is used to return the whole information of the job.
// 1 input
// "JobID"
// ============================================================================================================================
func (t *SimpleChaincode) QueryJobInfo(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1 ")
	}
	JobID := args[0]

	// Get the state from the ledger
	JobInfo, err := stub.GetState(JobID)
	if err != nil {
		jsonResp := "{\"Error\":\"Failed to get state for " + JobID + "\"}"
		return nil, errors.New(jsonResp)
	}

	if JobInfo == nil {
		jsonResp := "{\"Error\":\"Nil content for " + JobID + "\"}"
		return nil, errors.New(jsonResp)
	}

	return JobInfo, nil
}

// ============================================================================================================================
// QueryAgencyID function is used to query the agency`ID use the job`ID who published .
// 1 input
// "JobID"
// ============================================================================================================================
func (t *SimpleChaincode) QueryAgencyID(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1 ")
	}
	JobID := args[0]
	JobInfo, err := stub.GetState(JobID)

	//test if the job has been existed
	if err != nil {
		return nil, errors.New("The job never been exited")
	}
	if JobInfo == nil {
		return nil, errors.New("The job`s information is empty!")
	}

	var JobInfoJsonType JobInfoStruct //json type to accept the JobInfo from state

	err = json.Unmarshal(JobInfo, &JobInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	return []byte(JobInfoJsonType.UserID), nil
}

// ============================================================================================================================
// QuerySalary function is used to query the salary use the job`ID who published .
// 1 input
// "JobID"
// ============================================================================================================================
func (t *SimpleChaincode) QuerySalary(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1 ")
	}
	JobID := args[0]
	JobInfo, err := stub.GetState(JobID)

	//test if the job has been existed
	if err != nil {
		return nil, errors.New("The job never been exited")
	}
	if JobInfo == nil {
		return nil, errors.New("The job`s information is empty!")
	}

	var JobInfoJsonType JobInfoStruct //json type to accept the JobInfo from state

	err = json.Unmarshal(JobInfo, &JobInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	return []byte(JobInfoJsonType.JobDetail.Salary), nil
}

func main() {
	err := shim.Start(new(SimpleChaincode))
	if err != nil {
		fmt.Printf("Error starting Simple chaincode: %s", err)
	}
}
