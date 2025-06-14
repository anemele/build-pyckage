package main

import (
	"fmt"
	"os"
)

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
