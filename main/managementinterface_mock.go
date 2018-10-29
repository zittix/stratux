// +build mock

package main

import (
	"log"
	"net/http"
)

func handleShutdownRequest(w http.ResponseWriter, r *http.Request) {
	log.Printf("Shutdown request received")
}

func doReboot() {
	log.Printf("Reboot request received")
}
