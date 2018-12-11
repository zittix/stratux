// +build linux

package main

import (
	"syscall"
)

func system_uptime() (uint64, error) {
	info := syscall.Sysinfo_t{}
	err := syscall.Sysinfo(&info)
	if err == nil {
		return info.Uptime, nil
	} else {
		return 0, err
	}
}
