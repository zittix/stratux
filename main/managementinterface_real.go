// +build !mock

package main

import (
	"net/http"
	"syscall"
)

func handleShutdownRequest(w http.ResponseWriter, r *http.Request) {
	syscall.Sync()
	syscall.Reboot(syscall.LINUX_REBOOT_CMD_POWER_OFF)
	gracefulShutdown()
}

func doReboot() {
	syscall.Sync()
	syscall.Reboot(syscall.LINUX_REBOOT_CMD_RESTART)
	gracefulShutdown()
}
