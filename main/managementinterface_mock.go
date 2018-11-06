// +build mock

package main

import (
	"fmt"
	"log"
	"net/http"
)

type FakeSensor struct {
}

func (s FakeSensor) Close() {

}

var (
	myIMUReader      *FakeSensor
	myPressureReader *FakeSensor
	analysisLogger   *FakeSensor
)

func initI2CSensors() {
	myIMUReader = new(FakeSensor)
	myPressureReader = new(FakeSensor)
	analysisLogger = new(FakeSensor)
}

func CalibrateAHRS() {

}

func ResetAHRSGLoad() {

}

func CageAHRS() {

}

func getMinAccelDirection() (i int, err error) {
	err = fmt.Errorf("Not implemented")
	i = 0
	return i, err
}

func isAHRSInvalidValue(val float64) bool {
	return true
}

func handleShutdownRequest(w http.ResponseWriter, r *http.Request) {
	log.Printf("Shutdown request received")
}

func doReboot() {
	log.Printf("Reboot request received")
}
