package main

import (
	"archive/zip"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

func unzip(zipFilePath string, dest string) error {
	zf, err := zip.OpenReader(zipFilePath)
	if err != nil {
		return err
	}
	defer zf.Close()

	for _, f := range zf.File {
		rc, err := f.Open()
		if err != nil {
			return err
		}
		defer rc.Close()

		filePath := filepath.Join(dest, f.Name)

		if f.FileInfo().IsDir() {
			err = os.MkdirAll(filePath, f.Mode())
			if err != nil {
				return err
			}
			continue
		}

		err = os.MkdirAll(filepath.Dir(filePath), 0755)
		if err != nil {
			return err
		}
		w, err := os.Create(filePath)
		if err != nil {
			return err
		}
		defer w.Close()

		_, err = io.Copy(w, rc)
		if err != nil {
			return err
		}
	}

	fmt.Println("Unzipped", zipFilePath, "to", dest)
	return nil
}

func findPythonVersion(pyckagePath string) (string, error) {
	re, err := regexp.Compile(`pyckage-py(\d\.\d+).zip$`)
	if err != nil {
		return "", err
	}
	matches := re.FindStringSubmatch(pyckagePath)
	if len(matches) > 1 {
		return matches[1], nil
	}
	return "", fmt.Errorf("invalid pyckage file name")
}

var mirrors = []string{
	"https://www.python.org/downloads/",
	"https://mirrors.huaweicloud.com/python/",
	"https://mirrors.aliyun.com/python-release/windows/",
}

func findPythonEmbed(pyckagePath string) (string, error) {
	ver, err := findPythonVersion(pyckagePath)
	if err != nil {
		return "", err
	}
	pattern := filepath.Join(filepath.Dir(pyckagePath), fmt.Sprintf("python-%s.*-embed-amd64.zip", ver))
	matches, err := filepath.Glob(pattern)
	if err != nil {
		return "", err
	}
	if len(matches) == 0 {
		return ver, fmt.Errorf("not found python-embed")
	}
	return matches[len(matches)-1], nil
}

func loadPyckage(pyckagePath string) error {
	dest := filepath.Base(pyckagePath)
	dest = strings.TrimSuffix(dest, filepath.Ext(dest))

	err := unzip(pyckagePath, dest)
	if err != nil {
		return err
	}

	embedPath, err := findPythonEmbed(pyckagePath)
	if err != nil {
		fmt.Printf("Download python-embed %s from the following mirrors\n", embedPath)
		for _, mirror := range mirrors {
			fmt.Println("-", mirror)
		}
		fmt.Println()
		return err
	}
	err = unzip(embedPath, filepath.Join(dest, "bin"))
	if err != nil {
		return err
	}

	// init pyckage
	matches, err := filepath.Glob(filepath.Join(dest, "bin", "*._pth"))
	if err != nil || len(matches) != 1 {
		_pth := filepath.Join(dest, "bin", "lib._pth")
		err := os.WriteFile(_pth, []byte("../lib\n"), 0644)
		if err != nil {
			return err
		}
	} else {
		_pth := matches[0]
		file, err := os.OpenFile(_pth, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			return err
		}
		defer file.Close()

		_, err = io.WriteString(file, "\n../lib\n")
		if err != nil {
			return err
		}
	}
	fmt.Println("Initialized pyckage:", dest)

	return nil
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("requires <pyckage.zip>")
		return
	}
	pyckagePath := os.Args[1]
	err := loadPyckage(pyckagePath)
	if err != nil {
		fmt.Println("Error:", err)
	}
}
