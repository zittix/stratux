
ifeq "$(CIRCLECI)" "true"
	BUILDINFO=
	PLATFORMDEPENDENT=
else
	LDFLAGS_VERSION=-X main.stratuxVersion=`git describe --tags --abbrev=0` -X main.stratuxBuild=`git log -n 1 --pretty=%H`
	BUILDINFO=-ldflags "$(LDFLAGS_VERSION)"
	BUILDINFO_STATIC=-ldflags "-extldflags -static $(LDFLAGS_VERSION)"
#$(if $(GOROOT),,$(error GOROOT is not set!))
	PLATFORMDEPENDENT=fancontrol
endif

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
	TAGS=-tags mock
	MOCK_BUILD=1
	PLATFORMDEPENDENT=
else
	TAGS=""
	MOCK_BUILD=0
endif

all:
	make xdump978 xdump1090 xgen_gdl90 $(PLATFORMDEPENDENT)

xgen_gdl90:
	go get -t -d -v ./main ./godump978 ./uatparse ./sensors
	export CGO_CFLAGS_ALLOW="-L/Users/mathieu/Dropbox/stratux" && \
	cd main && \
	go build -o ../gen_gdl90 $(BUILDINFO) $(TAGS)

fancontrol:
	go get -t -d -v ./main
	go build $(BUILDINFO_STATIC) -p 4 main/fancontrol.go main/equations.go main/cputemp.go

xdump1090:
	#git submodule update --init
	cd dump1090 && make

xdump978:
	cd dump978 && make lib

.PHONY: test
test:
	make -C test

www:
	cd web && make

install:
	cp -f gen_gdl90 /usr/bin/gen_gdl90
	chmod 755 /usr/bin/gen_gdl90
	cp -f fancontrol /usr/bin/fancontrol
	chmod 755 /usr/bin/fancontrol
	-/usr/bin/fancontrol remove
	/usr/bin/fancontrol install
	cp image/10-stratux.rules /etc/udev/rules.d/10-stratux.rules
	cp image/99-uavionix.rules /etc/udev/rules.d/99-uavionix.rules
	rm -f /etc/init.d/stratux
	cp __lib__systemd__system__stratux.service /lib/systemd/system/stratux.service
	cp __root__stratux-pre-start.sh /root/stratux-pre-start.sh
	chmod 644 /lib/systemd/system/stratux.service
	chmod 744 /root/stratux-pre-start.sh
	ln -fs /lib/systemd/system/stratux.service /etc/systemd/system/multi-user.target.wants/stratux.service
	make www
	cp -f dump1090/dump1090 /usr/bin/
	cp -f image/hostapd_manager.sh /usr/sbin/
	cp -f image/stratux-wifi.sh /usr/sbin/
	if [ ! -d /usr/lib/stratux ]; then mkdir -p /usr/lib/stratux; fi
	cp -f main/plane_regs.sqlite3 /usr/lib/stratux/
	rm -f /var/run/ogn-rf.fifo
	mkfifo /var/run/ogn-rf.fifo
	cp -f ogn/rtlsdr-ogn/ogn-rf /usr/bin/
	chmod a+s /usr/bin/ogn-rf
	cp -f ogn/rtlsdr-ogn/ogn-decode /usr/bin/
	cp -f ./libdump978.so /usr/lib/libdump978.so

clean:
	rm -f gen_gdl90 libdump978.so fancontrol ahrs_approx
	cd dump1090 && make clean
	cd dump978 && make clean
