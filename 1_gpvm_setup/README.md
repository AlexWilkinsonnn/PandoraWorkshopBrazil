#  Getting Setup for Pandora Development on the DUNE gpvms

## 1. Work Area Setup

### SL7 container

```
/cvmfs/oasis.opensciencegrid.org/mis/apptainer/current/bin/apptainer shell --shell=/bin/bash -B /cvmfs,/exp,/nashome,/pnfs/dune,/opt,/run/user,/etc/hostname,/etc/hosts,/etc/krb5.conf --ipc --pid /cvmfs/singularity.opensciencegrid.org/fermilab/fnal-dev-sl7:latest
```

### VNC

Choose your favourite 2 digit number to be your port number. There will be a conflict if another user with the same favourite 2 digit number runs a VNC on the same server as you.

Open a tunnel from your chosen port number on the gpvm to your computer:
```
ssh -CKL 5901:localhost:59XX <username>@dunegpvmYY.fnal.gov
```

Edit the `VNCNUM` variable at the top of to your chosen 2 digit number `vnc_setup.sh`. Source this script on the gpvm:
```
$ source vnc_setup.sh 
vncserver :54 not running.  Starting now....

WARNING: vncserver has been replaced by a systemd unit and is now considered deprecated and removed in upstream.
Please read /usr/share/doc/tigervnc/HOWTO.md for more information.

New 'dunegpvm10.fnal.gov:54 (awilkins)' desktop is dunegpvm10.fnal.gov:54

Starting applications specified in /nashome/a/awilkins/.vnc/xstartup
Log file is /nashome/a/awilkins/.vnc/dunegpvm10.fnal.gov:54.log
```

Use a VNC viewer on your computer to view `localhost:5901`. TigerVNC is the default choice and I think macOS might come with one pre-installed.

When done with the VNC, make sure you stop the server:
```
vncserver -kill :XX
```

## 2. Building Pandora

Enter an SL7 container and copy the `.sh` scripts to where you want to build. Run the scripts in this order
```
$ source setup.sh
...
$ source clone.sh
...
$ source build_initial.sh
...
```
After this, whenever you make a change to an algorithm in `LArContent/` you only need to run `source build_larcontent.sh`
