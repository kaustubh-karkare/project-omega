package make

import (
	"encoding/json"
	"errors"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// PhaseNode is used to store the information of a phase
type PhaseNode struct {
	PhaseName  string   `json:"name"`
	Command    string   `json:"command"`
	Files      []string `json:"files"`
	Dependency []string `json:"deps"`
	Location   string
}

// PhaseNodeState stores the state of a phase node
type PhaseNodeState struct {
	PhaseNodeData PhaseNode
	Executed      bool
	Processing    bool
}

// GetBuildFileLocation finds the location of all build.json files
func GetBuildFileLocation() []string {

	fileList := []string{}
	filepath.Walk(".", func(path string, info os.FileInfo, err error) error {

		if info.IsDir() == true {
			return nil
		}
		
		// storing only the path to build.json files
		file := strings.Split(path, "/")
		fileName := file[len(file)-1]
		if fileName == "build.json" {
			fileList = append(fileList, path)
		}

		return nil
	})
	return fileList
}

// ParseJSON dumps the data from JSON file to PhaseNode
func ParseJSON(path string) ([]PhaseNode, error) {

	file, _ := ioutil.ReadFile(path)
	path = strings.Split(path, "build.json")[0]

	data := []PhaseNode{}
	err := json.Unmarshal([]byte(file), &data)

	if err == nil {
		for i := 0; i < len(data); i++ {
			data[i].Location = path
		}
	}

	return data, err
}

// DepthFirstSearch explores the dependency depth first
func (stateNode *PhaseNodeState) DepthFirstSearch(phases []PhaseNodeState) error {

	phaseNode := stateNode.PhaseNodeData
	// set Processing equal to true until all it's dependencies are not executed
	stateNode.Processing = true

	for id := 0; id < len(phaseNode.Dependency); id++ {
		deps := phaseNode.Dependency[id]
		for id2 := 0; id2 < len(phases); id2++ {

			if deps == phases[id2].PhaseNodeData.Location+phases[id2].PhaseNodeData.PhaseName {
				
				// If dependency is already in a processing state then it's a circular dependency
				if phases[id2].Processing == true {
					err := "Error: Circular dependency detected between " + phaseNode.PhaseName + " and " + deps
					return errors.New(err)
				} else if phases[id2].Executed == false {
					err := phases[id2].DepthFirstSearch(phases)
					if err != nil {
						return err
					}
				}
			}
		}
	}

	cmd := exec.Command("bash", "-c", stateNode.PhaseNodeData.Command)
	cmd.Dir = stateNode.PhaseNodeData.Location
	_, err := cmd.Output()
	if err != nil {
		return err
	}

	stateNode.Processing = false
	stateNode.Executed = true
	return nil
}

// ExecutePhase executes a phase along with it's dependencies
func ExecutePhase(phaseName string, phases []PhaseNodeState) error {

	for id := 0; id < len(phases); id++ {

		deps := phases[id].PhaseNodeData.Location + phases[id].PhaseNodeData.PhaseName
		if deps == phaseName {
			err := phases[id].DepthFirstSearch(phases)
			return err
		}
	}
	err := "Error: No phase named as " + phaseName + " found"
	return errors.New(err)
}

// Initialise creates the PhaseNodeState from Phase Nodes
func Initialise(fileList []string) ([]PhaseNodeState, error) {

	phases := make([]PhaseNodeState, 0)
	for id := 0; id < len(fileList); id++ {
		data, err := ParseJSON(fileList[id])
		if err != nil {
			return phases, err
		}

		for _, node := range data {
			var phaseState PhaseNodeState
			phaseState.PhaseNodeData = node
			phaseState.Executed = false
			phaseState.Processing = false

			phases = append(phases, phaseState)
		}
	}

	return phases, nil
}

// Make executes a phase after doing all the necessary setup
func Make(phaseName string) error {

	// Finding location of build.json files
	fileList := GetBuildFileLocation()

	// Building and intialising Phase Nodes
	phases, err := Initialise(fileList)
	if err != nil {
		return err
	}

	// Executing the required phase
	err = ExecutePhase(phaseName, phases)
	if err != nil {
		return err
	}

	return nil
}
