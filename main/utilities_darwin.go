// +build darwin

package main

import "errors"

func system_uptime() (uint64, error) {
	return 0, errors.New("Not available on OS X")
}
