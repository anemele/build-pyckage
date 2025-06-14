package main

import (
	"archive/zip"
	"fmt"
	"io"
	"os"
	"path/filepath"
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

	fmt.Println("Unzipped", zipFilePath, "==>", dest)
	return nil
}

// root entry point
// Given a pyckage file, unzip it and the corresponding python-embed file.
func loadPyckage(pyckagePath string) error {
	// remove the .zip suffix as the destination of unzipping
	if !strings.HasSuffix(pyckagePath, ".zip") {
		return fmt.Errorf("invalid pyckage file name")
	}
	dest := strings.TrimSuffix(pyckagePath, ".zip")

	err := unzip(pyckagePath, dest)
	if err != nil {
		return err
	}

	embedPath, err := findPythonEmbed(pyckagePath)
	// if find and download failed, let the user prepare the embed file manually.
	if err != nil {
		return err
	}

	// unzip the embed file to bin folder
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
	fmt.Println("Loaded pyckage:", dest)

	return nil
}
