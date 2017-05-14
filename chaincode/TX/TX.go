// ============================================================================================================================
// 本智能合约用于TX管理
// 功能包括：TX生成、查询，状态变更
// ============================================================================================================================

package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/hyperledger/fabric/core/chaincode/shim"
	"github.com/hyperledger/fabric/core/util"
	"strconv"
	"strings"
)

type SimpleChaincode struct {
}

// ============================================================================================================================
// TXInfo struct
// ============================================================================================================================
type TXInfoStruct struct {
	JobID       string
	UserID      string
	ApplyTime   string
	TxID        string
	Status      string
	StuScore    string
	AgencyScore string
}

func (t *SimpleChaincode) GetJobChaincodeToCall() string {
	chainCodeToCall := "7147861cb80f5447b0ee974bc917935cc8f65bd89a271095af7e0f7cb8184a7dccdbb93a43fce11d24c7532743c7d22c0fa68c6f6bbc29bb8a92f2e98b2d92ae"
	return chainCodeToCall
}

func (t *SimpleChaincode) GetUserChaincodeToCall() string {
	chainCodeToCall := "9d29747f0b642ed65f481fbc1132d518834b3099671ad5d86feb8609202197f26cefcca348942ce9facdbe8312b5d7ee5598a6d9522c34ae9755720c1176a598"
	return chainCodeToCall
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
	} else if function == "create" { //create a tx when a student applied a job and auto to check this application
		return t.Create(stub, args)
	} else if function == "artificialCheck" { //agency check this application when auto check not passed
		return t.ArtificialCheck(stub, args)
	} else if function == "evaluate" { //student and agancy evaluate each other
		return t.Evaluate(stub, args)
	}

	return nil, errors.New("Received unknown function invocation")
}

// ============================================================================================================================
// Create function is used to create a tx when a student applied a job and auto to check this application
// 2 input
// "TxID","TxInfo"
// ============================================================================================================================
func (t *SimpleChaincode) Create(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	TxID := args[0]
	TxInfo := args[1]
	TxTest, _ := stub.GetState(TxID)

	//test if the TX has been existed
	if TxTest != nil {
		return nil, errors.New("the Tx is existed")
	}

	// add the Tx
	err = stub.PutState(TxID, []byte(TxInfo))
	if err != nil {
		return nil, errors.New("Failed to add the user")
	}

	var TXInfoJsonType TXInfoStruct //json type to accept the TxInfo from state

	err = json.Unmarshal([]byte(TxInfo), &TXInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	//attach the TxID to related job
	//invoke JobInfo chaincode to add this TxID attach to the Job
	jobChainCodeToCall := t.GetJobChaincodeToCall()
	funcOfJobChaincode := "addTX"
	invokeArgsOfJobChaincode := util.ToChaincodeArgs(funcOfJobChaincode, TXInfoJsonType.JobID, TXInfoJsonType.TxID)
	response1, err := stub.InvokeChaincode(jobChainCodeToCall, invokeArgsOfJobChaincode)
	if err != nil {
		errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
		fmt.Printf(errStr)
		return nil, errors.New(errStr)
	}
	fmt.Printf("Invoke chaincode successful. Got response %s", string(response1))

	//addTotalApplied
	funcOfJobChaincode3 := "addTotalApplied"
	invokeArgsOfJobChaincode3 := util.ToChaincodeArgs(funcOfJobChaincode3, TXInfoJsonType.JobID)
	response3, err := stub.InvokeChaincode(jobChainCodeToCall, invokeArgsOfJobChaincode3)
	if err != nil {
		errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
		fmt.Printf(errStr)
		return nil, errors.New(errStr)
	}
	fmt.Printf("Invoke chaincode successful. Got response %s", string(response3))

	//attach the TxID to related student
	//invoke UserInfo chaincode to add this TxID attach to the student
	userChainCodeToCall := t.GetUserChaincodeToCall()
	funcOfUserChaincode := "addTX"
	invokeArgsOfUserChaincode := util.ToChaincodeArgs(funcOfUserChaincode, TXInfoJsonType.UserID, TXInfoJsonType.TxID)
	response2, err := stub.InvokeChaincode(userChainCodeToCall, invokeArgsOfUserChaincode)
	if err != nil {
		errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
		fmt.Printf(errStr)
		return nil, errors.New(errStr)
	}
	fmt.Printf("Invoke chaincode successful. Got response %s", string(response2))

	//auto check
	// Query User`s credit score
	f := "queryCurrentCreditScore"
	queryArgs := util.ToChaincodeArgs(f, TXInfoJsonType.UserID)
	response, err := stub.QueryChaincode(userChainCodeToCall, queryArgs)
	if err != nil {
		errStr := fmt.Sprintf("Failed to query chaincode. Got error: %s", err.Error())
		fmt.Printf(errStr)
		return nil, errors.New(errStr)
	}
	Score, err := strconv.Atoi(string(response))
	if err != nil {
		errStr := fmt.Sprintf("Error retrieving state from ledger for queried chaincode: %s", err.Error())
		fmt.Printf(errStr)
		return nil, errors.New(errStr)
	}
	if Score > 8 {
		TXInfoJsonType.Status = "已通过审核待评价"
		//addTotalHired
		invokeArgsOfJobChaincode5 := util.ToChaincodeArgs("addTotalHired", TXInfoJsonType.JobID)
		response5, err := stub.InvokeChaincode(jobChainCodeToCall, invokeArgsOfJobChaincode5)
		if err != nil {
			errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
			fmt.Printf(errStr)
			return nil, errors.New(errStr)
		}
		fmt.Printf("Invoke chaincode successful. Got response %s", string(response5))
	} else {
		TXInfoJsonType.Status = "未通过自动审核"
		//addTotalWaitCheck
		invokeArgsOfJobChaincode4 := util.ToChaincodeArgs("addTotalWaitCheck", TXInfoJsonType.JobID, "1")
		response4, err := stub.InvokeChaincode(jobChainCodeToCall, invokeArgsOfJobChaincode4)
		if err != nil {
			errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
			fmt.Printf(errStr)
			return nil, errors.New(errStr)
		}
		fmt.Printf("Invoke chaincode successful. Got response %s", string(response4))
	}

	// put the new TxInfo into state
	a, err := json.Marshal(TXInfoJsonType)
	if err != nil {
		return nil, err
	}
	// put the new score into state
	err = stub.PutState(TxID, a)
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// ArtificialCheck function is used to check this application when auto check not passed by agency
// 2 input
// "TxID","Result(1:通过；2:未通过)"
// ============================================================================================================================
func (t *SimpleChaincode) ArtificialCheck(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 2 {
		return nil, errors.New("Incorrect number of arguments. Expecting 2. ")
	}
	TxID := args[0]
	Result, _ := strconv.Atoi(args[1])
	TxInfo, err := stub.GetState(TxID)

	//test if the TX has been existed
	if err != nil {
		return nil, errors.New("The TX never been exited")
	}
	if TxInfo == nil {
		return nil, errors.New("The TX`s information is empty!")
	}

	var TXInfoJsonType TXInfoStruct //json type to accept the TxInfo from state

	err = json.Unmarshal(TxInfo, &TXInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	if strings.EqualFold(TXInfoJsonType.Status, "未通过自动审核") {
		if Result == 1 {
			TXInfoJsonType.Status = "已通过审核待评价"
			//addTotalHired
			jobChainCodeToCall := t.GetJobChaincodeToCall()
			invokeArgsOfJobChaincode9 := util.ToChaincodeArgs("addTotalHired", TXInfoJsonType.JobID)
			response9, err := stub.InvokeChaincode(jobChainCodeToCall, invokeArgsOfJobChaincode9)
			if err != nil {
				errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
				fmt.Printf(errStr)
				return nil, errors.New(errStr)
			}
			fmt.Printf("Invoke chaincode successful. Got response %s", string(response9))

		} else {
			TXInfoJsonType.Status = "未通过审核，已回绝"
		}
		//addTotalWaitCheck
		jobChainCodeToCall := t.GetJobChaincodeToCall()
		invokeArgsOfJobChaincode6 := util.ToChaincodeArgs("addTotalWaitCheck", TXInfoJsonType.JobID, "-1")
		response6, err := stub.InvokeChaincode(jobChainCodeToCall, invokeArgsOfJobChaincode6)
		if err != nil {
			errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
			fmt.Printf(errStr)
			return nil, errors.New(errStr)
		}
		fmt.Printf("Invoke chaincode successful. Got response %s", string(response6))
	} else {
		return nil, errors.New("Incorrect stage of status. Expecting 未通过自动审核. ")
	}

	// put the new TxInfo into state
	a, err := json.Marshal(TXInfoJsonType)
	if err != nil {
		return nil, err
	}
	// put the new score into state
	err = stub.PutState(TxID, a)
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}

	return nil, nil
}

// ============================================================================================================================
// Evaluate function is used to evaluate each other by student and agancy
// 3 input
// "TxID","UserID","Score"
// ============================================================================================================================
func (t *SimpleChaincode) Evaluate(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	var err error
	if len(args) != 3 {
		return nil, errors.New("Incorrect number of arguments. Expecting 3. ")
	}
	TxID := args[0]
	UserID := args[1]
	Score := args[2]

	TxInfo, err := stub.GetState(TxID)

	//test if the TX has been existed
	if err != nil {
		return nil, errors.New("The TX never been exited")
	}
	if TxInfo == nil {
		return nil, errors.New("The TX`s information is empty!")
	}

	var TXInfoJsonType TXInfoStruct //json type to accept the TxInfo from state

	err = json.Unmarshal(TxInfo, &TXInfoJsonType)
	if err != nil {
		fmt.Println("error:", err)
	}

	if strings.EqualFold(TXInfoJsonType.UserID, UserID) {
		TXInfoJsonType.AgencyScore = Score
	} else {
		TXInfoJsonType.StuScore = Score
	}

	f10 := "creditScoreEdit"
	invokeArgs10 := util.ToChaincodeArgs(f10, UserID, Score)
	response10, err := stub.InvokeChaincode(t.GetUserChaincodeToCall(), invokeArgs10)
	if err != nil {
		errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
		fmt.Printf(errStr)
		return nil, errors.New(errStr)
	}

	fmt.Printf("Invoke chaincode successful. Got response %s", string(response10))

	if len([]byte(TXInfoJsonType.StuScore)) != 0 && len([]byte(TXInfoJsonType.AgencyScore)) != 0 {
		StudentScore, _ := strconv.Atoi(TXInfoJsonType.StuScore)
		if StudentScore >= 8 {
			// Query agency`s ID
			f := "queryAgencyID"
			queryArgs := util.ToChaincodeArgs(f, TXInfoJsonType.JobID)
			AgencyID, err := stub.QueryChaincode(t.GetJobChaincodeToCall(), queryArgs)
			if err != nil {
				errStr := fmt.Sprintf("Failed to query chaincode. Got error: %s", err.Error())
				fmt.Printf(errStr)
				return nil, errors.New(errStr)
			}
			// Query salary
			f1 := "querySalary"
			queryArgs1 := util.ToChaincodeArgs(f1, TXInfoJsonType.JobID)
			Salary, err := stub.QueryChaincode(t.GetJobChaincodeToCall(), queryArgs1)
			if err != nil {
				errStr := fmt.Sprintf("Failed to query chaincode. Got error: %s", err.Error())
				fmt.Printf(errStr)
				return nil, errors.New(errStr)
			}

			f2 := "autoSettle"
			invokeArgs2 := util.ToChaincodeArgs(f2, TXInfoJsonType.UserID, string(AgencyID), string(Salary))
			response2, err := stub.InvokeChaincode(t.GetUserChaincodeToCall(), invokeArgs2)
			if err != nil {
				errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
				fmt.Printf(errStr)
				return nil, errors.New(errStr)
			}

			fmt.Printf("Invoke chaincode successful. Got response %s", string(response2))

			TXInfoJsonType.Status = "已结算"
			//addTotalSettled
			jobChainCodeToCall := t.GetJobChaincodeToCall()
			invokeArgsOfJobChaincode7 := util.ToChaincodeArgs("addTotalSettled", TXInfoJsonType.JobID)
			response7, err := stub.InvokeChaincode(jobChainCodeToCall, invokeArgsOfJobChaincode7)
			if err != nil {
				errStr := fmt.Sprintf("Failed to invoke chaincode. Got error: %s", err.Error())
				fmt.Printf(errStr)
				return nil, errors.New(errStr)
			}
			fmt.Printf("Invoke chaincode successful. Got response %s", string(response7))
		} else {
			TXInfoJsonType.Status = "已评价未通过自动结算"
		}
	} else {
		// put the new TxInfo into state
		a, err := json.Marshal(TXInfoJsonType)
		if err != nil {
			return nil, err
		}
		// put the new score into state
		err = stub.PutState(TxID, a)
		if err != nil {
			return nil, errors.New("Failed to putstate")
		}
		return nil, nil
	}

	// put the new TxInfo into state
	a, err := json.Marshal(TXInfoJsonType)
	if err != nil {
		return nil, err
	}
	// put the new score into state
	err = stub.PutState(TxID, a)
	if err != nil {
		return nil, errors.New("Failed to putstate")
	}
	return nil, nil

}

// ============================================================================================================================
// Query function is the entry point for Queries
// ============================================================================================================================
func (t *SimpleChaincode) Query(stub shim.ChaincodeStubInterface, function string, args []string) ([]byte, error) {

	if function == "queryTxInfo" {
		return t.QueryTxInfo(stub, args)
	}

	return nil, errors.New("failed to query")

}

// ============================================================================================================================
// QueryTxInfo function is used to query the Tx`s information.
// 1 input
// "TxID"
// ============================================================================================================================
func (t *SimpleChaincode) QueryTxInfo(stub shim.ChaincodeStubInterface, args []string) ([]byte, error) {
	if len(args) != 1 {
		return nil, errors.New("Incorrect number of arguments. Expecting 1 ")
	}
	TxID := args[0]

	// Get the state from the ledger
	TxInfo, err := stub.GetState(TxID)
	if err != nil {
		jsonResp := "{\"Error\":\"Failed to get state for " + TxID + "\"}"
		return nil, errors.New(jsonResp)
	}

	if TxInfo == nil {
		jsonResp := "{\"Error\":\"Nil content for " + TxID + "\"}"
		return nil, errors.New(jsonResp)
	}

	return TxInfo, nil
}

func main() {
	err := shim.Start(new(SimpleChaincode))
	if err != nil {
		fmt.Printf("Error starting Simple chaincode: %s", err)
	}
}
