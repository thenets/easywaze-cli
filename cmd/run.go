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

package cmd

import (
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	"github.com/fatih/color"
	"github.com/spf13/cobra"
	tools "github.com/thenets/brasilio-cli/cmd/tools"
)

// runCmd represents the run command
var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Executa o(s) script(s) para obtenção de dados",
	Long: `Executa o script de obtenção de dados e gera os 
arquivos CSV como saída.

Verifique se todos os arquivos estão dentro do diretório 'src':
(o número no início do arquivo determina a ordem de execução)
- ./meu-projeto/src/01-extrator-magistrados.py
- ./meu-projeto/src/02-extrator-juizes.py
- ./meu-projeto/src/03-extrator-politicos.py

Além disso, os arquivos deverão ser enviados para o diretório 'package':
- ./meu-projeto/package/magistrados.csv
- ./meu-projeto/package/juizes.csv
- ./meu-projeto/package/politicos.csv`,
	Run: func(cmd *cobra.Command, args []string) {
		tools.CreateDependenciesPaths()

		// Get current path
		currentPath, err := os.Getwd()
		if err != nil {
			log.Fatal(err)
		}

		// Custom run script
		runScriptPath := currentPath + "/run.sh"
		if _, err := os.Stat(runScriptPath); err == nil {
			tools.CopyFile(runScriptPath, currentPath+"/.brasilio/run.sh")
		}

		// Python dependencies
		pythonRequirementsPath := currentPath + "/requirements.txt"
		if _, err := os.Stat(pythonRequirementsPath); err == nil {
			tools.CopyFile(pythonRequirementsPath, currentPath+"/.brasilio/requirements.txt")
		}

		// Benchmark
		start := time.Now()

		// Run command in a new process
		processName := "brasilio-build"
		cmdStr := tools.GetDockerCommand(processName)
		exitCode := tools.NewCmdProcess(cmdStr, processName)

		// Benchmark and exit message
		elapsed := strconv.FormatFloat(time.Since(start).Seconds(), 'f', 4, 64)
		if exitCode == 0 {
			color.Cyan(fmt.Sprintf("\n[DONE] [CODE %d] Time %ss\n", exitCode, elapsed))
		} else {
			color.HiYellow(fmt.Sprintf("\n[ERROR] [CODE %d] Time %ss\n", exitCode, elapsed))
		}
	},
}

func init() {
	rootCmd.AddCommand(runCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// runCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// runCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
