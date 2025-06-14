/*
Process embed version of Python release.

Given a Python version with major and minor, find the embed file.
For example, given 3.8, find the embed file python-3.8.10-embed-amd64.zip.
If there are multiple embed files, return the latest one.
If there are no embed files, trying downloading from the web, if fails return error.
*/
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
)

// embed python is in {pyckagePath}/_embed
const _embedPath = "_embed"

// Find the Python version from the pyckage file name.
// For example, given abc-0.1.0-pyckage-py3.12.zip returns 3.12
func parsePythonVersion(pyckageName string) (string, error) {
	re, err := regexp.Compile(`pyckage-py(\d\.\d+).zip$`)
	if err != nil {
		return "", err
	}
	matches := re.FindStringSubmatch(pyckageName)
	if len(matches) > 1 {
		return matches[1], nil
	}
	return "", fmt.Errorf("invalid pyckage file name")
}

// Find the embed file from the pyckage file name.
func findPythonEmbed(pyckagePath string) (string, error) {
	pyver, err := parsePythonVersion(filepath.Base(pyckagePath))
	if err != nil {
		return "", err
	}

	pykgDir := filepath.Dir(pyckagePath)
	embedDir := filepath.Join(pykgDir, _embedPath)
	// If embed directory does not exist, create it.
	if _, err := os.Stat(embedDir); os.IsNotExist(err) {
		err = os.Mkdir(embedDir, 0755)
		if err != nil {
			return "", err
		}
	}

	pattern := filepath.Join(embedDir, fmt.Sprintf("python-%s.*-embed-amd64.zip", pyver))
	matches, err := filepath.Glob(pattern)
	if err != nil {
		return "", err
	}
	if len(matches) > 0 {
		// If multiple embed files, return the latest one.
		// TODO: If this code works? Which one is the latest, 3.8.10 or 3.8.9?
		// NOTE: It is unnecessary to use the latest one.
		return matches[len(matches)-1], nil
	}

	// If no embed files, trying downloading from the web.
	embedPath, err := downloadPythonEmbed(pyver, embedDir)
	if err != nil {
		absPath, _ := filepath.Abs(embedDir)
		displayDownloadURL(absPath)
		return "", err
	}

	return embedPath, nil
}
