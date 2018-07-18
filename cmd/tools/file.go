// Copyright © 2018 Luiz Felipe F M Costa <luiz@thenets.org>
// 
// MIT License
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

package tools

import (
	"fmt"
	"io"
	"os"
)

// CopyFile copy static files.
// Example: CopyFile("/tmp/source.txt", "/tmp/destiny.txt")
func CopyFile(srcPath string, destPath string) {
	srcFile, err := os.Open(srcPath)
	check(err)
	defer srcFile.Close()

	destFile, err := os.Create(destPath) // creates if file doesn't exist
	check(err)
	defer destFile.Close()

	_, err = io.Copy(destFile, srcFile) // check first var for number of bytes copied
	check(err)

	err = destFile.Sync()
	check(err)
}

func check(err error) {
	if err != nil {
		fmt.Printf("Error : %s\n", err.Error())
		os.Exit(1)
	}
}
