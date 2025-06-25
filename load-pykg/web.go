package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
)

// Websites that host Python releases
var ftpMirrors = []string{
	"https://mirrors.huaweicloud.com/python/",
	"https://www.python.org/ftp/python/",
	// aliyun mirror has different website structure, do not use it.
	// "https://mirrors.aliyun.com/python-release/windows/",
}

// latest releases that with binary builds
// See: https://devguide.python.org/versions/
var latestReleasesMap = map[string]string{
	"3.8":  "3.8.10",  // https://peps.python.org/pep-0569/
	"3.9":  "3.9.13",  // https://peps.python.org/pep-0596/
	"3.10": "3.10.11", // https://peps.python.org/pep-0619/
	"3.11": "3.11.9",  // https://peps.python.org/pep-0664/
	"3.12": "3.12.10", // https://peps.python.org/pep-0693/
	"3.13": "3.13.5",  // https://peps.python.org/pep-0719/
}

// Get the embed Python release from the web.
func getPythonEmbedUrl(pyver string) (string, error) {
	ver, ok := latestReleasesMap[pyver]
	if !ok {
		return "", fmt.Errorf("invalid Python version")
	}
	for _, mirror := range ftpMirrors {
		url := fmt.Sprintf("%s%s/python-%s-embed-amd64.zip", mirror, ver, ver)
		req, _ := http.NewRequest("HEAD", url, nil)
		req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0")
		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			continue
		}
		if resp.StatusCode == 200 {
			return url, nil
		}
	}
	return "", fmt.Errorf("not found python-embed")
}

// Download the embed Python release from the web.
func downloadPythonEmbed(pyver string, embedDir string) (string, error) {
	embedUrl, err := getPythonEmbedUrl(pyver)
	if err != nil {
		return "", err
	}

	// build a request
	request, err := http.NewRequest("GET", embedUrl, nil)
	// to avoid 418 error
	request.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0")
	if err != nil {
		return "", err
	}

	resp, err := http.DefaultClient.Do(request)
	if err != nil {
		return "", err
	}
	if resp.StatusCode != 200 {
		return "", fmt.Errorf("invalid status code: %d", resp.StatusCode)
	}

	// open local file
	embedPath := filepath.Join(embedDir, filepath.Base(embedUrl))
	w, err := os.Create(embedPath)
	if err != nil {
		return "", err
	}
	defer w.Close()

	// copy the response body to local file
	fmt.Printf("Downloading %s ==> %s\n", embedUrl, embedPath)
	_, err = io.Copy(w, resp.Body)
	if err != nil {
		return "", err
	}

	return embedPath, nil
}

// Display where to download the embed Python release
// and where to place it.
func displayDownloadURL(place string) {
	fmt.Println("Download python-embed from the following mirrors")
	for _, mirror := range ftpMirrors {
		fmt.Println("-", mirror)
	}
	fmt.Println("  and move it to", place)
}
