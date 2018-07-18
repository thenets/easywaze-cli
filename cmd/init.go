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
	"os"
	"os/exec"

	"github.com/thenets/brasilio-cli/cmd/tools"

	"github.com/spf13/cobra"
)

// initCmd represents the init command
var initCmd = &cobra.Command{
	Use:   "init",
	Short: "Inicia um novo projeto do Brasil.io",
	Long: `O novo projeto do Brasil.io terá tudo que será necessário para começar
a desenvolver um novo código de extração e/ou tratamento de dados.

Um código em Python será criado como exemplo para ajudar na criação de um 'datapackage'.`,
	Run: func(cmd *cobra.Command, args []string) {
		// Check if has argument
		if len(args) != 1 {
			fmt.Println("ERROR: É necessário informar o nome do novo projeto.")
			fmt.Println("Execute 'brasilio init --help' para mais detalhes.")
			os.Exit(0)
		}

		// Check if Docker is available
		if tools.IsCommandAvailable("docker") == false {
			fmt.Println("ERROR: 'docker' não está instalado.")
			fmt.Println("Acesse https://docs.docker.com/install/ para mais informações.")
			os.Exit(0)
		}

		// Check if Git is available
		if tools.IsCommandAvailable("git") == false {
			fmt.Println("ERROR: 'git' não está instalado.")
			fmt.Println("Acesse https://git-scm.com/downloads para mais informações.")
			os.Exit(0)
		}

		// Check if project already exist
		if _, err := os.Stat(args[0]); err == nil {
			fmt.Printf("ERROR: o projeto '%s' já existe!\n", args[0])
			fmt.Println(tools.GetSupportMessage())
			os.Exit(0)
		}

		// Clone new project
		shellCmd := exec.Command("git", "clone", "https://github.com/thenets/brasilio-package", args[0])
		shellCmd.Stdout = os.Stdout
		shellCmd.Stderr = os.Stderr
		if err := shellCmd.Run(); err != nil {
			fmt.Println(tools.GetSupportMessage())
			os.Exit(0)
		}

		// Remove git reference
		os.RemoveAll(args[0] + "/.git")

		fmt.Printf("\n[DONE] Projeto '%s' criado!\n", args[0])
		fmt.Printf("[TIP ] Entre no diretório 'cd %s' e execute 'brasilio run' para começar! :)\n", args[0])

	},
}

func init() {
	rootCmd.AddCommand(initCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// initCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// initCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
