package make

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// BuildRule is used to store the information of a phase
type BuildRule struct {
	RuleName  string   `json:"name"`
	Command    string   `json:"command"`
	Files      []string `json:"files"`
	Dependency []string `json:"deps"`
	Location   string
}

// BuildRuleNode stores the information of a BuildRule for efficient retrieval
type BuildRuleNode struct {
	RuleName  string
	Command    string
	Files      map[string]bool
	Dependency map[string]bool
	Location   string
}

// NodeState stores the state of a BuildRule Node
type NodeState struct {
	NodeData BuildRuleNode
	Executed      bool
	Processing    bool
	FilesModified bool
}

// GetBuildFileLocation finds the location of all build.json files
func GetBuildFileLocation(root, buildFilename string) []string {

	fileList := []string{}
	if root == "" {
		root = "./"
	}
	filepath.Walk(root, func(path string, info os.FileInfo, err error) error {

		if info.IsDir() == true {
			return nil
		}

		// storing only the path to build.json files
		file := strings.Split(path, "/")
		fileName := file[len(file)-1]
		if fileName == buildFilename {
			fileList = append(fileList, path)
		}

		return nil
	})
	return fileList
}

// ParseJSON dumps the data from JSON file to BuildRule structure
func ParseJSON(path, buildFilename string) ([]BuildRule, error) {

	file, _ := ioutil.ReadFile(path)
	path = strings.Split(path, buildFilename)[0]

	JSONbuildRuleData := []BuildRule{}
	err := json.Unmarshal([]byte(file), &JSONbuildRuleData)

	if err == nil {
		for id := 0; id < len(JSONbuildRuleData); id++ {
			JSONbuildRuleData[id].Location = path
		}
	}

	return JSONbuildRuleData, err
}

// DepthFirstSearch explores the dependency depth first
func DepthFirstSearch(root string, currentBuildNode NodeState, nodeMap map[string]NodeState) ([]string, error) {

	currentNodeData := currentBuildNode.NodeData
	// set Processing equal to true until all it's dependencies are not executed
	currentBuildNode.Processing = true
	nodeMap[currentNodeData.Location + currentNodeData.RuleName] = currentBuildNode

	var dependentFiles []string
	for file := range currentNodeData.Files {
		dependentFiles = append(dependentFiles, currentNodeData.Location + file)
	}

	for dependencyName := range currentNodeData.Dependency {

		dependencyNode, FoundDependency := nodeMap[currentNodeData.Location + dependencyName]
		if FoundDependency == true {

			// If dependency is already in a processing state then it's a circular dependency
			if dependencyNode.Processing == true {
				err := "Error: Circular dependency detected between " + currentNodeData.RuleName + " and " + dependencyName
				return dependentFiles, errors.New(err)
			} else if dependencyNode.Executed == false {
				delete(nodeMap, dependencyName)
				files, err := DepthFirstSearch(root, dependencyNode, nodeMap)
				if err != nil {
					return dependentFiles, err
				}

				for _, file := range files {
					dependentFiles = append(dependentFiles, file)
				}
			}
		}
	}

	cmd := exec.Command("bash", "-c", currentBuildNode.NodeData.Command)
	// Executing command from this directory
	cmd.Dir = root + currentBuildNode.NodeData.Location
	_, err := cmd.Output()
	if err != nil {
		return dependentFiles, err
	}

	delete(nodeMap, currentNodeData.Location + currentNodeData.RuleName)
	currentBuildNode.Processing = false
	currentBuildNode.Executed = true
	nodeMap[currentNodeData.Location + currentNodeData.RuleName] = currentBuildNode
	return dependentFiles, nil
}

// ExecutePhase executes a phase along with it's dependencies
func ExecutePhase(root, runPhase string, nodeMap map[string]NodeState) ([]string, error) {

	node, foundPhase := nodeMap[runPhase]

	if foundPhase == true {
		delete(nodeMap, runPhase)
		dependentFiles, err := DepthFirstSearch(root, node, nodeMap)
		return dependentFiles, err
	}
	err := "Error: No phase named as " + runPhase + " found"
	return nil, errors.New(err)
}

// ReDepthFirstSearch executes Builds associated with modified files
func ReDepthFirstSearch(root string, currentBuildNode NodeState, modifiedFiles map[string]bool, nodeMap map[string]NodeState) error {

	currentNodeData := currentBuildNode.NodeData
	// set Processing equal to true until all it's dependencies are not executed
	currentBuildNode.Processing = true
	nodeMap[currentNodeData.Location+currentNodeData.RuleName] = currentBuildNode

	var dependentFiles []string
	// checks if current build is directly associated with any modified files
	for file := range currentNodeData.Files {
		dependentFiles = append(dependentFiles, currentNodeData.Location+file)
		_, foundModifiedFiles := modifiedFiles[currentNodeData.Location+file]

		if currentBuildNode.FilesModified == false && foundModifiedFiles == true {
			currentBuildNode.FilesModified = true
		}
	}

	for dependencyName := range currentNodeData.Dependency {

		dependencyNode, FoundDependency := nodeMap[dependencyName]
		if FoundDependency == true {

			// If dependency is already in a processing state then it's a circular dependency
			if dependencyNode.Processing == true {
				err := "Error: Circular dependency detected between " + currentNodeData.RuleName + " and " + dependencyName
				return errors.New(err)
			} else if dependencyNode.Executed == false {
				delete(nodeMap, dependencyName)
				err := ReDepthFirstSearch(root, dependencyNode, modifiedFiles, nodeMap)
				if err != nil {
					return err
				}
				
				// checks if current build is indirectly associated with any modified files
				if currentBuildNode.FilesModified == false && nodeMap[dependencyName].FilesModified == true {
					currentBuildNode.FilesModified = true
				}
			}
		}
	}

	// Executes a build command realted to a Build if it's assocaited with modified files directly or indirectly
	if currentBuildNode.FilesModified == true {
		cmd := exec.Command("bash", "-c", currentBuildNode.NodeData.Command)
		cmd.Dir = root + currentBuildNode.NodeData.Location
		_, err := cmd.Output()
		if err != nil {
			return err
		}
	}

	delete(nodeMap, currentNodeData.Location+currentNodeData.RuleName)
	currentBuildNode.Processing = false
	currentBuildNode.Executed = true
	nodeMap[currentNodeData.Location+currentNodeData.RuleName] = currentBuildNode
	return nil
}

// ReExecutePhase executes the phases that are associated with recent modified files
func ReExecutePhase(root, runPhase string, modifiedFiles map[string]bool, nodeMap map[string]NodeState) error {

	node, foundPhase := nodeMap[runPhase]
	if foundPhase == true {
		delete(nodeMap, runPhase)
		err := ReDepthFirstSearch(root, node, modifiedFiles, nodeMap)
		return err
	}

	err := "Error: No phase named as " + runPhase + " found"
	return errors.New(err)
}

// CreateBuildRuleNode creates a new node out of a Build Rule
func CreateBuildRuleNode(root string, node BuildRule) NodeState {

	var nodeState NodeState
	nodeState.NodeData.RuleName = node.RuleName
	nodeState.NodeData.Command = node.Command
	if root == "" {
		nodeState.NodeData.Location = node.Location
	} else {
		nodeState.NodeData.Location = strings.Split(node.Location, root)[1]
	}
	nodeState.NodeData.Files = make(map[string]bool)
	nodeState.NodeData.Dependency = make(map[string]bool)
	nodeState.Executed = false
	nodeState.Processing = false

	for _, filename := range node.Files {
		nodeState.NodeData.Files[filename] = true
	}
	for _, dependencyName := range node.Dependency {
		nodeState.NodeData.Dependency[dependencyName] = true
	}

	return nodeState
}

// Initialise creates the NodeState using Build Data
func Initialise(root string, buildFilename string, buildFileList []string) (map[string]NodeState, error) {

	nodeMap := make(map[string]NodeState)
	for id := 0; id < len(buildFileList); id++ {
		JSONbuildRuleData, err := ParseJSON(buildFileList[id], buildFilename)
		if err != nil {
			return nodeMap, err
		}

		for _, node := range JSONbuildRuleData {
			nodeState := CreateBuildRuleNode(root, node)
			// Mapping BuildRules' name (w.r.t its Location) to respective node state
			nodeMap[nodeState.NodeData.Location + nodeState.NodeData.RuleName] = nodeState
		}
	}

	return nodeMap, nil
}

// ExecuteWatch executes the watch feature in Build tool
func ExecuteWatch(root string, waitTime int, dependentFiles map[string]time.Time, nodeMap map[string]NodeState, runPhases []string) error {

	var err error
	// Keeping a constant watch on Files involved in execution of required Phases
	for err == nil {

		// Sleep induced for |waitTime| seconds
		time.Sleep(time.Duration(waitTime) * time.Second)

		modifiedFiles := make(map[string]bool)
		// Check for all modified files
		for file, modTime := range dependentFiles {
			fileInfo, _ := os.Stat(root + file)
			currentModTime := fileInfo.ModTime()
			if modTime != currentModTime {
				modifiedFiles[file] = true
				dependentFiles[file] = currentModTime
			}
		}

		// Initalising the nodes
		if len(modifiedFiles) != 0 {

			for RuleName, NodeState := range nodeMap {
				NodeState.Executed = false
				NodeState.Processing = false
				NodeState.FilesModified = false
				nodeMap[RuleName] = NodeState
			}

			for _, runPhase := range runPhases {
				err := ReExecutePhase(root, runPhase, modifiedFiles, nodeMap)
				if err != nil {
					break;
				}
				fmt.Println(runPhase, ": ReExecuted Successfully")
			}
		} else {
			fmt.Println("No Files Modified!")
		}
	}

	return err
}

// Make executes a phase after doing all the necessary setup
func Make(root, buildFilename string, waitTime int, watch bool, runPhases []string) error {

	if root == "./" {
		root = ""
	}

	// Finding location of all build files w.r.t to root's location
	buildFileList := GetBuildFileLocation(root, buildFilename)

	// Intialising the BuildRule as Nodes and Mapping the BuildRule's Node name to Node state 
	nodeMap, err := Initialise(root, buildFilename, buildFileList)
	if err != nil {
		return err
	}

	// depndentFiles map the files involved in execution of required Phases to their modification time
	dependentFiles := make(map[string]time.Time)
	// Executing the required Phases
	for _, runPhase := range runPhases {
		Files, err := ExecutePhase(root, runPhase, nodeMap)
		if err != nil {
			return err
		}
		fmt.Println(runPhase, ": Executed Successfully")
		for _, file := range Files {
			fileInfo, _ := os.Stat(root + file)
			dependentFiles[file] = fileInfo.ModTime()
		}
	}

	if watch == true {
		err := ExecuteWatch(root, waitTime, dependentFiles, nodeMap, runPhases)
		return err
	}

	return nil
}
