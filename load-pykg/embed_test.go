package main

import (
	"testing"
)

func Test_findPythonVersion(t *testing.T) {
	ver, err := parsePythonVersion("abc-0.1.0-pyckage-py3.12.zip")
	if err != nil {
		t.Error(err)
	}
	if ver != "3.12" {
		t.Error("invalid version")
	}
}
