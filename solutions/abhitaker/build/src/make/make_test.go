package make

import (
	"fmt"
	"os"
	"testing"
)

func TestGetBuildFileLocation(t *testing.T) {

	testcases := []struct {
		input  []string
		expect []string
	}{
		{[]string{"", "foo/", "bar/"}, []string{"build.json", "foo/build.json", "bar/build.json"}},
	}

	for _, testcase := range testcases {

		for _, path := range testcase.input {

			os.Mkdir(path, os.ModePerm)
			var file, err = os.Create(path + "build.json")
			if err != nil {
				fmt.Println(err)
				return
			}
			defer file.Close()

		}

		output := GetBuildFileLocation("", "build.json")

		if len(testcase.expect) != len(output) {
			t.Errorf("yo Expected Output not matches the actual Output")
		}

		for _, fileloc := range testcase.expect {
			found := 0
			for _, path := range output {
				if fileloc == path {
					found = 1
					break
				}
			}
			if found == 0 {
				t.Errorf("Expected Output not matches the actual Output")
			}
		}

	}
}
