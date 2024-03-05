# -*- rpm-spec -*-

# Note: This spec file is largely shared with the public virtio-win drivers
# shipped on fedora sites. The canonical location is here:
#
# https://github.com/virtio-win/virtio-win-pkg-scripts
#
# If you make any changes to this file that affect the RPM content (but not
# version numbers or changelogs, etc), submit a patch to the upstream spec.

%global virtio_win_prewhql_build virtio-win-prewhql-0.1-242
%global qemu_ga_win_build qemu-ga-win-106.0.1-1.el9
%global qxl_build qxl-win-unsigned-0.1-24
%global spice_vdagent_build 0.10.0-5.el8
%global qxlwddm_build spice-qxl-wddm-dod-0.21-2.el8

%global windows_installer_version -1.9.36-0
%global winfsp_version -1.12.22339

Summary: VirtIO para-virtualized drivers for Windows(R)
Name: virtio-win
Version: 1.9.36
Release: 0%{?dist}
Group: Applications/System
License: Apache-2.0 AND BSD-3-Clause AND GPL-2.0-only AND GPL-2.0-or-later
URL: http://www.redhat.com/
BuildArch: noarch

# Already built/ files
Source1: %{name}-%{version}-bin-for-rpm.tar.gz
Source2: %{qemu_ga_win_build}.noarch.rpm

# Source files shipped in the srpm
Source3: %{virtio_win_prewhql_build}-sources.zip
Source4: mingw-%{qemu_ga_win_build}.src.rpm
Source5: %{qxl_build}-sources.zip
Source6: %{qxlwddm_build}.src.rpm
Source7: %{qxlwddm_build}.noarch.rpm
Source8: spice-vdagent-win-%{spice_vdagent_build}.src.rpm
Source9: spice-vdagent-win-x64-%{spice_vdagent_build}.noarch.rpm
Source10: spice-vdagent-win-x86-%{spice_vdagent_build}.noarch.rpm
Source11: winfsp%{winfsp_version}-sources.zip


Source20: virtio-win-guest-tools.exe
Source21: virtio-win-gt-x86.msi
Source22: virtio-win-gt-x64.msi
%if 0%{?fedora}
Source23: virtio-win-guest-tools-installer-%{version}.tar.gz
%else
Source23: virtio-win-installer%{windows_installer_version}-sources.zip
%endif
Source24: winfsp%{winfsp_version}.msi

%if 0%{?rhel}
Source70: virtio-win-pre-installable-drivers-win-7.xml
Source71: virtio-win-pre-installable-drivers-win-8.xml
Source72: virtio-win-pre-installable-drivers-win-8.1.xml
Source73: virtio-win-pre-installable-drivers-win-10.xml
Source74: virtio-win-pre-installable-drivers-win-11.xml
Source80: agents.json
%endif

BuildRequires: /usr/bin/mkisofs


%description
VirtIO para-virtualized Windows(R) drivers for 32-bit and 64-bit
Windows(R) guests.


%prep
%setup -q -T -b 1 -n %{name}-%{version}

# Extract qemu-ga RPM
mkdir -p iso-content/guest-agent
mkdir -p %{qemu_ga_win_build}
pushd %{qemu_ga_win_build}/ && rpm2cpio %{SOURCE2} | cpio -idmv
popd

%{__mv} %{qemu_ga_win_build}/usr/i686-w64-mingw32/sys-root/mingw/bin/qemu-ga-i386.msi iso-content/guest-agent/
%{__mv} %{qemu_ga_win_build}/usr/x86_64-w64-mingw32/sys-root/mingw/bin/qemu-ga-x86_64.msi iso-content/guest-agent/


# Extract spice-vdagent RPMs
mkdir -p iso-content/spice-vdagent
mkdir -p %{spice_vdagent_build}
pushd %{spice_vdagent_build}/ && rpm2cpio %{SOURCE9} | cpio -idmv
popd
pushd %{spice_vdagent_build}/ && rpm2cpio %{SOURCE10} | cpio -idmv
popd

%{__mv} %{spice_vdagent_build}/usr/share/spice/spice-vdagent-x64-*.msi iso-content/spice-vdagent/spice-vdagent-x64.msi
%{__mv} %{spice_vdagent_build}/usr/share/spice/spice-vdagent-x86-*.msi iso-content/spice-vdagent/spice-vdagent-x86.msi

# Extract qxlwddm drivers
mkdir -p iso-content/qxl-wddm-dod
mkdir -p %{qxl_wddm_dod}
pushd %{qxl_wddm_dod}/ && rpm2cpio %{SOURCE7} | cpio -idmv
popd

%{__mv} %{qxl_wddm_dod}/usr/share/spice/QxlWddmDod_*_x64.msi iso-content/qxl-wddm-dod/QxlWddmDod_x64.msi
%{__mv} %{qxl_wddm_dod}/usr/share/spice/QxlWddmDod_*_x86.msi iso-content/qxl-wddm-dod/QxlWddmDod_x86.msi


# Move virtio-win MSIs into place
%{__cp} %{SOURCE20} iso-content/
%{__cp} %{SOURCE21} iso-content/
%{__cp} %{SOURCE22} iso-content/
%{__cp} %{SOURCE24} iso-content/


%if 0%{?rhel} > 7
# Dropping unsupported Windows versions.
# It's done here to fix two issues at the same time: do not
# release them in iso AND as binary drivers.
for srcdir in iso-content rpm-drivers; do
    rm_driver_dir() {
        find $srcdir -type d -name $1 -print0 | xargs -0 rm -rf
    }

    # ISO naming
    rm_driver_dir xp
    rm_driver_dir 2k3
    rm_driver_dir 2k8
    rm_driver_dir smbus

    # Old floppy naming
    rm_driver_dir WinXP
    rm_driver_dir Win2003
    rm_driver_dir Win2008
done
%endif


%build
# Generate .iso
pushd iso-content
/usr/bin/mkisofs \
    -o ../media/%{name}-%{version}.iso \
    -r -iso-level 4 \
    -input-charset iso8859-1 \
    -allow-lowercase \
    -relaxed-filenames \
    -V "%{name}-%{version}" .
popd


%install
%{__install} -d -m0755 %{buildroot}%{_datadir}/%{name}

add_link() {
    # Adds name-version$1 to datadir, with a non-versioned symlink
    %{__install} -p -m0644 media/%{name}-%{version}$1 %{buildroot}%{_datadir}/%{name}
    %{__ln_s} %{name}-%{version}$1 %{buildroot}%{_datadir}/%{name}/%{name}$1
}

# Install .iso, create non-versioned symlink
add_link .iso

# RHEL-8 does not support vfd images
%if 0%{?rhel} <= 7
add_link _x86.vfd
add_link _amd64.vfd
add_link _servers_x86.vfd
add_link _servers_amd64.vfd
%endif

%if 0%{?rhel}
%{__mkdir} -p %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-7.d/
%{__cp} %{SOURCE70} %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-7.d/

%{__mkdir} -p %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-8.d/
%{__cp} %{SOURCE71} %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-8.d/

%{__mkdir} -p %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-8.1.d/
%{__cp} %{SOURCE72} %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-8.1.d/

%{__mkdir} -p %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-10.d/
%{__cp} %{SOURCE73} %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-10.d/

%{__mkdir} -p %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-11.d/
%{__cp} %{SOURCE74} %{buildroot}/%{_datadir}/osinfo/os/microsoft.com/win-11.d/
%endif

%{__cp} -a rpm-drivers %{buildroot}/%{_datadir}/%{name}/drivers

%if 0%{?rhel}
%{__cp} %{SOURCE80} %{buildroot}/%{_datadir}/%{name}/
%{__cp} iso-content/data/*.json %{buildroot}/%{_datadir}/%{name}/
%endif

# Copy the guest agent .msi into final RPM location
%{__mkdir} -p %{buildroot}%{_datadir}/%{name}/guest-agent/
%{__install} -p -m0644 iso-content/guest-agent/qemu-ga-i386.msi %{buildroot}%{_datadir}/%{name}/guest-agent/qemu-ga-i386.msi
%{__install} -p -m0644 iso-content/guest-agent/qemu-ga-x86_64.msi  %{buildroot}%{_datadir}/%{name}/guest-agent/qemu-ga-x86_64.msi

%{__mkdir} -p %{buildroot}%{_datadir}/%{name}/spice-vdagent/
%{__install} -p -m0644 iso-content/spice-vdagent/spice-vdagent-x86.msi %{buildroot}%{_datadir}/%{name}/spice-vdagent/spice-vdagent-x86.msi
%{__install} -p -m0644 iso-content/spice-vdagent/spice-vdagent-x64.msi  %{buildroot}%{_datadir}/%{name}/spice-vdagent/spice-vdagent-x64.msi

%{__mkdir} -p %{buildroot}%{_datadir}/%{name}/qxl-wddm-dod/
%{__install} -p -m0644 iso-content/qxl-wddm-dod/QxlWddmDod_x86.msi %{buildroot}%{_datadir}/%{name}/qxl-wddm-dod/QxlWddmDod_x86.msi
%{__install} -p -m0644 iso-content/qxl-wddm-dod/QxlWddmDod_x64.msi  %{buildroot}%{_datadir}/%{name}/qxl-wddm-dod/QxlWddmDod_x64.msi

# Copy virtio-win install .msi into final RPM location
%{__mkdir} -p %{buildroot}%{_datadir}/%{name}/installer/
%{__install} -p -m0644 iso-content/virtio-win-guest-tools.exe %{buildroot}%{_datadir}/%{name}/installer/
%{__install} -p -m0644 iso-content/virtio-win-gt-x86.msi %{buildroot}%{_datadir}/%{name}/installer/
%{__install} -p -m0644 iso-content/virtio-win-gt-x64.msi  %{buildroot}%{_datadir}/%{name}/installer/
%{__install} -p -m0644 iso-content/winfsp%{winfsp_version}.msi %{buildroot}%{_datadir}/%{name}/installer/

%files
%doc iso-content/virtio-win_license.txt
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/%{name}-%{version}.iso
%{_datadir}/%{name}/%{name}.iso
%{_datadir}/%{name}/guest-agent/*.msi
%{_datadir}/%{name}/spice-vdagent/*.msi
%{_datadir}/%{name}/qxl-wddm-dod/*.msi

%{_datadir}/%{name}/drivers/i386
%{_datadir}/%{name}/drivers/amd64

# Add some by-os and by-driver whitelisting, so unintended things don't
# sneak into the hierarchy
%{_datadir}/%{name}/drivers/by-driver/Balloon
%{_datadir}/%{name}/drivers/by-driver/NetKVM
%{_datadir}/%{name}/drivers/by-driver/pvpanic
%{_datadir}/%{name}/drivers/by-driver/qemufwcfg
%{_datadir}/%{name}/drivers/by-driver/qemupciserial
%{_datadir}/%{name}/drivers/by-driver/qxl
%{_datadir}/%{name}/drivers/by-driver/vioinput
%{_datadir}/%{name}/drivers/by-driver/viorng
%{_datadir}/%{name}/drivers/by-driver/vioscsi
%{_datadir}/%{name}/drivers/by-driver/vioserial
%{_datadir}/%{name}/drivers/by-driver/viostor
%{_datadir}/%{name}/drivers/by-driver/viofs
%{_datadir}/%{name}/drivers/by-driver/sriov
%{_datadir}/%{name}/drivers/by-driver/qxldod
%{_datadir}/%{name}/drivers/by-driver/viogpudo
%{_datadir}/%{name}/drivers/by-driver/fwcfg
%exclude %{_datadir}/%{name}/drivers/by-driver/virtio-win_license.txt
%if 0%{?fedora}
%{_datadir}/%{name}/drivers/by-driver/smbus
%endif

%{_datadir}/%{name}/drivers/by-os/i386
%{_datadir}/%{name}/drivers/by-os/amd64
%if 0%{?fedora}
%{_datadir}/%{name}/drivers/by-os/ARM64
%endif

%if 0%{?rhel} <= 7
%{_datadir}/%{name}/*.vfd
%endif

%{_datadir}/%{name}/installer/*.msi
%{_datadir}/%{name}/installer/*.exe

# osinfo-db drop-in files
%if 0%{?rhel}
%{_datadir}/osinfo/os/microsoft.com/win-7.d/virtio-win-pre-installable-drivers-win-7.xml
%{_datadir}/osinfo/os/microsoft.com/win-8.d/virtio-win-pre-installable-drivers-win-8.xml
%{_datadir}/osinfo/os/microsoft.com/win-8.1.d/virtio-win-pre-installable-drivers-win-8.1.xml
%{_datadir}/osinfo/os/microsoft.com/win-10.d/virtio-win-pre-installable-drivers-win-10.xml
%{_datadir}/osinfo/os/microsoft.com/win-11.d/virtio-win-pre-installable-drivers-win-11.xml
%endif

# .json files
%if 0%{?rhel}
%{_datadir}/%{name}/*.json
%endif

%changelog
* Sun Dec 10 2023 Vadim Rozenfeld <vrozenfe@redhat.com>
- Update installer 1.9.36.0 with the latest agents RHEL-9.3.0.Z
- Related: #18403

* Sun Aug 27 2023 Vadim Rozenfeld <vrozenfe@redhat.com>
- Update installer 1.9.35.0 with the latest agents RHEL-9.3.0
- Related: #420

* Sat Jul 10 2023 Vadim Rozenfeld <vrozenfe@redhat.com>
- Update installer 1.9.34.0 with the latest agents RHEL-9.3.0
- Related: #420

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Jan 20 2021 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.15-2.el9
- This is a plain copy of the virtio-win package released in RHEL-8.3.1 for RHEL-9.0.0
- Resolves: rhbz#1916284

* Tue Jan 19 2021 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.15-1.el9
- This is a plain copy of the virtio-win package released in RHEL-8.3.1 for RHEL-9.0.0
- Resolves: rhbz#1916284

* Tue Jan 5 2021 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.15-0.el8
- Update to build 191 
- Update installer 1.9.15.1 with the latest agents and drivers
- Resolves: rhbz#1911903

* Fri Sep 25 2020 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.14-4.el8
- Update installer 1.9.14.2 with the latest agents
- Resolves: rhbz#1746667

* Wed Sep 23 2020 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.14-3.el8
- Update installer 1.9.14.2
- Resolves: rhbz#1746667

* Mon Sep 21 2020 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.14-2.el8
- Update installer 1.9.14.1
- Resolves: rhbz#1746667

* Thu Sep 17 2020 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.14-1.el8
- Update installer 1.9.13.1
- Resolves: rhbz#1746667


* Mon Sep 14 2020 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.14-0.el8
- Update to qemu and spice agents.
- Update qxl-dod driver
- add sriov drivers
- Resolves: rhbz#1746667
- Resolves: rhbz#1787022

* Sat Sep 5 2020 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.13-1.el8
- Update to build 189
- Resolves: rhbz#1746667
- Resolves: rhbz#1787022

* Mon Aug 3 2020 Vadim Rozenfeld <vrozenfe@redhat.com> - 1.9.12-2.el8
- Fix a typo in virtio-win.spec file
- Resolves: rhbz#1814530

* Tue Mar 10 2020 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.11-1.el8
- Resolves: rhbz#1790455
  (Add guest-get-devices command to qemu-ga-win)
- Resolves: rhbz#1802452
- Resolves: rhbz#1791147
- Resolves: rhbz#1794609
- Resolves: rhbz#1791153
- Resolves: rhbz#1788042
- Resolves: rhbz#1785544
- Resolves: rhbz#1785522
- Resolves: rhbz#1783953
- Resolves: rhbz#1783906
- Resolves: rhbz#1783880
- Resolves: rhbz#1782370
- Resolves: rhbz#1711743
- Resolves: rhbz#1745818
- Resolves: rhbz#1549602
- Resolves: rhbz#1549597
- Resolves: rhbz#1549596
- Resolves: rhbz#1549595
- Resolves: rhbz#1549577

* Thu Dec 19 2019 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.10-3.el8
- Resolves: rhbz#1784745
  ([virto-win] virtio input drivers are not installed via virtio-win-installer)
- Resolves: rhbz#1784744
  ([virtio-win] guest can not boot up due to virtio-win-installer remove option uninstalls all drivers including OS driver)
- Resolves: rhbz#1784760
  ([virtio-win] drivers can not be installed via virtio-win-installer on win2012 guest)

* Tue Dec 17 2019 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.10-2.el8
- Include the installers
- Resolves: rhbz#1745298
  ([RFE] Add installer to virtio-win iso)

* Mon Dec 16 2019 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.10-1.el8
- Update to build 173
- Resolves: rhbz#1754822
  ([virtio-win][viostor] Add TRIM support. )

* Mon Dec 02 2019 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.10-0.el8
- Resolves: rhbz#1771814
  (QEMU Guest Agent's version is not correct which is still the old one. )
- Resolves: rhbz#1751431
  ("guest-get-memory-block-info" is enabled but in fact it is not currently supported )
- Resolves: rhbz#1733165
  (QEMU Guest Agent For Windows Return Garbled NIC Name )
- Resolves: rhbz#1754822
  ([virtio-win][viostor] Add TRIM support. )

* Fri Aug 30 2019 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.9-3.el8
- Resolves: rhbz#1588425
  (virtio-mouse can not passthrough)

* Fri Aug 30 2019 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.9-2
- Resolves: rhbz#1588425
  (virtio-mouse can not passthrough)

* Wed Aug 28 2019 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.9-1.el8
- Resolves: rhbz#1588425
  (virtio-mouse can not passthrough)

* Mon Jul 01 2019 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.8-7.el8
- Resolves: rhbz#1715121
  (Move virtio-win to regular RHEL channel)

* Tue Sep 11 2018 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.6-4
- Resolves: BZ#1353099
  During the fix for 1353099, the smbus become empty. So it needs to be
  removed.

* Tue Sep 11 2018 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.6-3
- Resolves: BZ#1353099
  Drop unsupported Windows releases from virtio-win

- Resolves: BZ#1533540
  Drop floppy (.vfd) files from virtio-win

* Fri Aug 24 2018 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.6-1
- Rebase virtio-win based on RHEL-7.6

* Mon Aug 13 2018 Troy Dawson <tdawson@redhat.com> - 1.9.3-3
- Release Bumped for el8 Mass Rebuild

* Thu Dec 07 2017 Danilo C. L. de Paula <ddepaula@redhat.com> - 1.9.3-2
- This is a plain copy of the virtio-win package released in RHEL-7.4 for RHEL-8.0

* Tue Aug 01 2017 Danilo Cesar Lemes de Paula <ddepaula@redhat.com> - 1.9.3-1

- Resolves: BZ#1473575
  [virtio-win][netkvm] win2012R2 BSOD after migration during netperf test

* Thu Jul 20 2017 Danilo Cesar Lemes de Paula <ddepaula@redhat.com> - 1.9.2-0

- Resolves: BZ#1471073
  Latest latest virtio driver (network) for Windows drops lots of packets (edit)

* Wed Jun 7 2017 Danilo Cesar Lemes de Paula <ddepaula@redhat.com> - 1.9.1-0

This release contains the following drivers and build number:
 - pvpanic, build 137
 - vioinput, build 137
 - vioser, build 137
 - balloon, build 13
 - viorng, build 137
 - netkvm, build 139
 - vioscsi, build 136
 - viostor, build 136
 - qxl, build qxl-win-unsigned-0.1-24
 - qemupciserial, build 137
 - smbus, build 138
 - qemufwcfg, build 128


This release addresses the following BZs:
- Resolves: BZ#1075292
  ([virtio-win][qemu-ga-win] qemu guest agent should report correctly error description (windows guest))
- Resolves: BZ#1202267
  ([virtio-win][wddm-qxl]The display of guest change to black-white mode after s4 on win8.1-32)
- Resolves: BZ#1218449
  (Ship qemupciserial.cat on the iso)
- Resolves: BZ#1256626
  (windows guest(win7/win10)  CTRL_VLAN=on/off  does not support for  virtio-net-pci)
- Resolves: BZ#1303510
  (Change the copyright on all the Windows drivers to "2017" in virtio-win-prewhql build)
- Resolves: BZ#1357406
  (Add virtio-input Windows guest driver)
- Resolves: BZ#1369353
  (virtio_balloon: backport "available memory" stat support)
- Resolves: BZ#1370351
  ([virtio-win][vioser] serial port can not transfer data when nr>=31)
- Resolves: BZ#1372174
  (NIC device cannot start when boot a Win10 guest with multiple queues(256 queues))
- Resolves: BZ#1374725
  (Output command {"execute": "guest-info"} includes unsupported qemu-ga-win commands)
- Resolves: BZ#1387125
  (QEMU guest agent VSS Provider is crashed after snapshot deletion)
- Resolves: BZ#1388775
  ([virtio-win][vioinput]guest bsod[DRIVER_PAGE_FAULT_IN_FREED_SPECIAL_POOL (d5)] when run virtio-input whql jobs)
- Resolves: BZ#1388920
  ([NetKVM] review additional possible performance improvements)
- Resolves: BZ#1389125
  (viostor extend viostor driver with STORAGE_REQUEST_BLOCK support)
- Resolves: BZ#1389445
  (VirtIO library interface incompatiblity with NetKvm (bool definition))
- Resolves: BZ#1390714
  ([RFE] [virtio-win] Add fw_cfg device in windows guest in order to make svvp test pass)
- Resolves: BZ#1391844
  ([virtio-win][balloon][viorng][virtio-input] cannot install balloon, viorng and virtio-input driver successfully on win10-32 and win8.1-32(build 127))
- Resolves: BZ#1392693
  ([virtio-win][vioser][whql] job "PCI Hardware Compliance Test For a Single Device(PCIHCT)" fail w/ "-M q35")
- Resolves: BZ#1392719
  ([virtio-win][vioser]can't install serial driver successfuly on win10-64 guest with q35 machine type(build 128))
- Resolves: BZ#1392819
  ([NetKVM] Race between ParaNdis_SetupRSSQueueMap and ParaNdis6_SendNetBufferLists due to the lack of synchronisation)
- Resolves: BZ#1393140
  ([virtio-win][vioser][whql]BSOD when running job "WDF Logo Test-Final" w/ q35 on win2008-32)
- Resolves: BZ#1393772
  (New unknown device "SM Bus Controller" shows in system device manager after booting with q35)
- Resolves: BZ#1395790
  (vioscsi.sys BSOD when adding CPU to live Windows Server 2012R2 guest)
- Resolves: BZ#1402496
  (Balloon: Stats don't work if balloon driver is disabled when blnsvr service starts)
- Resolves: BZ#1406271
  ([virtio-win][qemu-ga-win] if guest is auto-released after 10s, the following "guest-fsfreeze-freeze" and "guest-fsfreeze-thaw" should not prompt error.)
- Resolves: BZ#1408771
  ([virtio-win][viorng] Guest win2008-32 occurs BSoD when running job "WDF Logo Tests - Final" under q35)
- Resolves: BZ#1408901
  ([virtio-win][whql][vioinput] Many jobs failed on win2012R2/ws2016 when running w/o GUI)
- Resolves: BZ#1409298
  ([virtio-win][balloon] Guest win2008-32 occurs BSoD when running job 'Device Path Exerciser')
- Resolves: BZ#1411092
  (4K virtual drives broken on Windows)
- Resolves: BZ#1411596
  (Virtio driver of network device works abnormally when convert win2008 x86 guest from kvm to rhev by virt-v2v)
- Resolves: BZ#1412067
  ([virtio-win][whql][netkvm] job 1c_IOCTLCoverage failed.)
- Resolves: BZ#1419785
  ([virtio-win][whql][balloon] Guest WIN8-32 occured BSOD in job "DF - PNP Stop (Rebalance) Device Test (Certification)")
- Resolves: BZ#1419854
  (vioinput: Driver is dropping rapid input events)
- Resolves: BZ#1419900
  (BSOD of vioser.sys on Win10 in S0->S4->S0 flow)
- Resolves: BZ#1421258
  (Add qemufwcfg driver to virtio-win)
- Resolves: BZ#1421988
  ([virtio-win][virtio-input] Read wrong device in guest's device manager when do hot-plug a mouse device and keyboard device)
- Resolves: BZ#1425967
  (Update qemupciserial.* files for virtio-win)
- Resolves: BZ#1426482
  ([virtio-win][balloon] cost too much time when continues enlarge/evict during playing video)
- Resolves: BZ#1429807
  ([virtio-win][whql][netkvm] guests bsod(d1) when running job "NDISTest 6.0 - [1 Machine] - 1c_FaultHandling")
- Resolves: BZ#1431561
  ([NetKVM] Implement VIRTIO_NET_F_GUEST_ANNOUNCE feature in Windows virtio-net driver - IPv6)
- Resolves: BZ#1432567
  ([virtio-win][vioscsi] Crash dump not generated with num_queues=4)
- Resolves: BZ#1433266
  ([virtio-win][netkvm] cannot launch anti-virus software(ESET Endpoint Antivirus) with virtio NetKVM driver)
- Resolves: BZ#1433830
  ([virtio-win][whql][netkvm] guests bsod(d1) when running job "NDISTest 6.5 - [2 Machine] - OffloadLSO")
- Resolves: BZ#1434316
  ([qemu-ga-win] Guest agent might hang if VSS service is stoped during freeze)
- Resolves: BZ#1435778
  (virtio-serial breaks when CPU hot added to Windows Server 2008R2 Datacenter)
- Resolves: BZ#1438410
  (Net-KVM: Add VlanId property to Inf file)
- Resolves: BZ#1439085
  ([virtio-win][netkvm] Guest win2008-32 failed in job Ethernet - NDISTest 6.0 with 1c_wmicoverage failure)
- Resolves: BZ#1441595
  ([virtio-win][viostor]windows 2016 can not generate dump file on AMD host)
- Resolves: BZ#1442322
  ([virtio-win][viostor]Cannot enlarge/shrink disk with virtio-blk-pci device.)
- Resolves: BZ#1443019
  ([virtio-win][qemupciserial] job "PNP Rebanlance RequestNew Resources Device Test" and other two jobs failed on win10+ guests)
- Resolves: BZ#1444271
  ([virtio-win][viorng]job "DF - InfVerif INF Verification" failed on HLK 1703)
- Resolves: BZ#1451652
  (RFE: Add smbus driver to virtio-win)
- Resolves: BZ#1456403
  (Net-KVM: Implement MTU report feature of the virtio-net device)

* Mon Sep 19 2016 Yash Mankad <ymankad@redhat.com> - 1.9.0-3

Add Windows 2016 drivers to .vfd files
Updates copyright notice in virtio-win_license.txt file (bz#1303511)

See the changelog entry for 1.9.0-1 for a full description
of the changes in this release.

- Resolves: bz#1340571
  (Add Windows 2k16 drivers to virtio-win)
- Resolves: bz#1303511
  (update copyright of license.txt file in virtio-win-1.7.5-0.el6 to 2016)

* Wed Sep 14 2016 Yash Mankad <ymankad@redhat.com> - 1.9.0-2

This release updates the VirtIO Block and Serial drivers for
Windows 10 and 2016 release to use the 126 build.

See the changelog entry for 1.9.0-1 for a full description
of the changes in this release.

- Resolves: bz#1340571
  (Add Windows 2k16 drivers to virtio-win)

* Tue Sep 13 2016 Yash Mankad <ymankad@redhat.com> - 1.9.0-1

- The virtio-win-1.9.0-1 release contains:
  - support for Windows 2016
  - Bugfixes and improvements (see below for bugzilla list)

- The drivers contained in this release are:
  - pvpanic build 121
  - Balloon build 125
  - viorng  build 125
  - viostor build 125 (Win 10 and 2016) and 126 (all others)
  - NetKVM  build 126
  - vioser  build 125 (Win 10 and 2016) and 126 (all others)
  - vioscsi build 124

- Also included in this release are:
  - qemu guest agent 7.3.2-1
  - qxl 0.1-24

This release addresses the following BZs:
- Resolves: bz#950611
  ([NetKVM] Pass WHQL tests with RSC feature enabled )
- Resolves: bz#954183
  ([NetKVM] Static driver verifier fails with NetKVM )
- Resolves: bz#1013336
  ([virtio-win][netkvm] BSoD occurs when running NDISTest6.5 -[2 Machine] - MPE_Ethernet job on windows 2012 (Win10))
- Resolves: bz#1122364
  ([virtio-win][vioser][rhel6]win2k8r2 guest bsod(7e) when do continuous hotplug/unplug during virtio serial in use with driver verifier enabled)
- Resolves: bz#1157987
  (Windows hangs at startup if virtio-scsi device is configured with vectors=1, 2, and 3)
- Resolves: bz#1161453
  ([whql][vioscsi]Job named by SCSI Compliance Test (LOGO) failed on win2k8-R2 and win8-64 guest)
- Resolves: bz#1190960
  ([whql][netkvm][mq]job failed due to "Received some net buffer lists out of order" w/ 4 queues)
- Resolves: bz#1208465
  (Windows guest boots up slowly with multiple virtual NIC devices (I attached 232 with mutifunction=on))
- Resolves: bz#1210166
  ([vioscsi] Add multiqueue support to Windows virtio-scsi driver.)
- Resolves: bz#1214177
  ([virtio-win] [NetKVM] Compilation errors with Visual Studio 2015 while trying to compile NetKVM)
- Resolves: bz#1214568
  ([RFE][virtio-win] Add WMI facility to check the virito-scsi mq enabled)
- Resolves: bz#1219841
  ([RFE] vioscsi.sys should support MS Cluster Services)
- Resolves: bz#1223426
  ([NetKVM] Performance degradation with multi-queue)
- Resolves: bz#1234741
  ([virtio-win][vioscsi]win2012 guest bsod(c9) when whql test DPWLK-HotAdd(1104) job)
- Resolves: bz#1234751
  ([virtio-win][vioscsi]win2012R2 guest bsod(d1) when whql test DPWLK-HotAdd(1104) job)
- Resolves: bz#1235108
  ([virtio-win][vioscsi]VIOSCSI driver is not signed by redhat certification on win200832/64 platform)
- Resolves: bz#1237024
  ([virtio-win][netkvm]ipv6 uploading speed is quite slow when set "TCP/UDP checksum offload(IPv6)" to "Rx & Tx Enabled")
- Resolves: bz#1241986
  (win7 64bit BSOD when booting it on RHEL7.2 host)
- Resolves: bz#1243229
  ([virtio-win][scsi][windows 10]win10 and win2016 guests bsod with D1 when run job "Bus Reset Test")
- Resolves: bz#1245957
  ([WHQL][viostor][data-plane]it could not generate dump file on WIN2008-32/64 via WLK while running Crash Dump job)
- Resolves: bz#1246993
  ([virtio-win][svvp][ws2016] job "Signed Driver Check (CheckLogo)" failed during ws2016 svvp test)
- Resolves: bz#1247006
  ([virtio-win][svvp][ws2016] job "Profile Interrupt Test" failed during ws2016 svvp test)
- Resolves: bz#1248873
  ([whql][netkvm]Job named NDISTest6.5-InvalidPackets failed with HCK on win8-32/win8-64(build 106))
- Resolves: bz#1248977
  ([virtio-win][vioscsi] Cannot install vioscsi driver on win7-32&win2008-32)
- Resolves: bz#1249867
  ([WHQL][vioscsi]Job hangs and it cannot continure on windows2008 guest via WLK)
- Resolves: bz#1250854
  ([WHQL][vioscsi]The job named crash dump failed on windows 2008 -32/64 platform)
- Resolves: bz#1256583
  (Win10 guest can't get ip address from dhcpserver when add mrg_rxbuf=off for virtio-net-pci)
- Resolves: bz#1266340
  ([whql][netkvm]NDISTest6.5 Manual test failed and generate dump file on windows 2008 guest)
- Resolves: bz#1270149
  ([virtio-win][netkvm] Check guest network link status of virtio nic with status=on failed (build 110))
- Resolves: bz#1289406
  ([virtio-win][vioser] Cannot install vioser driver successfully)
- Resolves: bz#1292788
  ([virtio-win][viostor] Cannot install viostor driver on win7-64&win2008-64&win2008R2)
- Resolves: bz#1293042
  ([virtio-win][vioser] Extra '-' (dash) in serial driver name)
- Resolves: bz#1293249
  ([virtio-win][vioser] IOCTL_GET_INFORMATION does not return required buffer size)
- Resolves: bz#1296092
  ([virtio-win][balloon] balloon driver can not be installed automately via pnputil)
- Resolves: bz#1303511
  (update copyright of license.txt file in virtio-win to 2016)
- Resolves: bz#1303809
  (provide QEMU guest agent command for setting root/administrator account password - window guests)
- Resolves: bz#1303988
  ([virtio-win] [virtio-1] [RFE] Add Virtio-1.0 support for NetKVM)
- Resolves: bz#1304041
  ([virtio-win] [virtio-1] [RFE] Add Virtio-1.0 support for vioserial)
- Resolves: bz#1304044
  ([virtio-win] [virtio-1] [RFE] Add Virtio-1.0 support for vioscsi)
- Resolves: bz#1304049
  ([virtio-win] [virtio-1] [RFE] Add Virtio-1.0 support for viostor)
- Resolves: bz#1313243
  ([virtio-win][netkvm][rhel6]win2008-32 guest bsod with HARDWARE_INTERRUP_STORM(f2) when running netperf for longevity test)
- Resolves: bz#1313887
  ([RFE] provide QEMU guest agent command for setting root account password (Windows guest) [rhel-7.3])
- Resolves: bz#1315984
  ([virtio-win] [virtio-1] [RFE] Add Virtio-1.0 support for baloon)
- Resolves: bz#1315985
  ([virtio-win] [virtio-1] [RFE] Add Virtio-1.0 support for rng)
- Resolves: bz#1321774
  ([virtio-win][vioscsi]fio jobs keep printing "0% done" in win2012r2 guest)
- Resolves: bz#1325078
  (Add TargetOSVersion to driver inf files)
- Resolves: bz#1328275
  (virtio-win doesn't provide windows 10 drivers within vfd [rhel-7.3])
- Resolves: bz#1334736
  (On the LAN network, as long as the VMs receive the Network message, and will always blue screen.)
- Resolves: bz#1336368
  ([virtio-win][viostor][virtio1.0]Cannot enlarge/shrink disk with virtio1.0 device)
- Resolves: bz#1339175
  ([NetKVM] Turn on RSC feature in NetKVM driver)
- Resolves: bz#1340571
  (Add Windows 2k16 drivers to virtio-win)
- Resolves: bz#1352432
  ([virtio-win][vioscsi]Win2012-64&R2 guest occurred bsod(d1) when whql test DPWLK- Hot-Replace - Device Test - Verify driver support for D3 power state)
- Resolves: bz#1352517
  ([virtio-win][balloon][whql]windows guest BSOD when run several WHQL jobs)
- Resolves: bz#1352809
  ([virtio-win][viorng]wrong dervier version for virtio-win-prewhql-121)
- Resolves: bz#1356363
  ([virtio-win][viorng] cannot install viorng driver on win2008-32/64 (build 122) )
- Resolves: bz#1358125
  (Virtio 1.0 driver didn't work on win10 with q35 machine type)
- Resolves: bz#1359072
  ([virtio-win][netkvm][whql]many whql jobs occurred BSOD(DRIVER_VERIFIER_DETECTED_VIOLATION (c4)) on build 122)
- Resolves: bz#1361501
  ([virtio-win][balloon] report "VCRUNTIME120.dll is missing from your computer"error when using blnsvr.exe)

* Fri Jun 10 2016 Yash Mankad <ymankad@redhat.com> - 1.8.0-5

Add Windows 10 drivers to .vfd files (bz#1328275)
Updates copyright notice in virtio-win_license.txt file to 2016 (bz#1303511)

 - Resolves: bz#1328275
   (virtio-win doesn't provide windows 10 drivers within vfd)
 - Resolves: bz#1303511
   (update copyright of license.txt file in virtio-win-1.7.5-0.el6 to 2016)

* Tue Oct 13 2015 Jeff E. Nelson <jen@redhat.com> - 1.8.0-4

Drop /vioscsi/w10/amd64/vioscsi.DVL.XML which was included
by mistake.

See the changelog entry for 1.8.0-1 for a full
description of the changes in this release.

- Resolves: bz#1217644
  (use hardlinks for .iso and /usr/share/virtio-win/drivers)

* Mon Oct 12 2015 Jeff E. Nelson <jen@redhat.com> - 1.8.0-3

Update virtio-win-1.8.0-for-rpm.tar.gz with the latest
signed drivers. This corrects packaging mistakes that put
drivers into the wrong directories; there are no new
bugfixes.

See the changelog entry for 1.8.0-1 for a full
description of the changes in this release.

- Resolves: bz#1217644
  (use hardlinks for .iso and /usr/share/virtio-win/drivers)

* Fri Oct  2 2015 Jeff E. Nelson <jen@redhat.com> - 1.8.0-2

The virtio-win-VVV-bin-for-rpm.zip file was previously a
zip file. This has been switched to a .tar.gz file which
provides better compresion and support for hard links.

- Resolves: bz#1217644
  (use hardlinks for .iso and /usr/share/virtio-win/drivers)

* Thu Oct  1 2015 Jeff E. Nelson <jen@redhat.com> - 1.8.0-1

- The virtio-win-1.8.0-1 release contains:
  - support for Windows 10
  - a new driver (pvpanic)
  - Bugfixes and improvements (see below for bugzilla list)

- The drivers contained in this release are:
  - pvpanic build 103
  - Balloon build 105
  - viorng  build 105
  - viostor build 106
  - NetKVM  build 105 (Windows Server 2008) and build 110 (all others)
  - vioser  build 108
  - vioscsi build 102

- Also included in this release are:
  - qemu guest agent 7.0-10
  - qxl 0.1-24

This release addresses the following BZs:
- Solves: bz#996479
  (RFE:pvpanic driver for windows guest)
- Solves: bz#1010887
  ([virtio-win][balloon] Guest display did not show properly after hibernate guest(s4)& resume after enlarging memory during runtime)
- Solves: bz#1017817
  (copying of 10+ MB plaintext from guest through spice clipboard to client results in: vio_serial write completion error 554)
- Solves: bz#1037949
  ([virtio-win][viostor]guest bsod(9F) when do s4 while guest running iozone)
- Solves: bz#1054640
  ([virtio-win][netkvm]windows 8.1 x86 BSOD on DRIVER_POWER_STATE_FAILURE (9f))
- Solves: bz#1058115
  ([whql][netkvm]win2k8-32 BSOD with code 9F when run WLK job "Ethernet - NDISTest 6.5 (MPE)")
- Solves: bz#1058121
  ([whql][netkvm]win2k8-32 BSOD with 7E code when run WLK job "Ethernet - NDISTest 6.5 (MPE)")
- Solves: bz#1058225
  ([WHQL][netkvm]Job named PM_PowerStateTransition failed because error pop up while test app's running on win8/win8.1)
- Solves: bz#1067249
  ([virtio-win][balloon]Balloon device can not be removed after blnsrv service installed)
- Solves: bz#1085702
  ([WHQL][netkvm][macvtap][1 machine]OffloadRsc failed on win2012 and win8-64 guest)
- Solves: bz#1096505
  ([NetKVM] Implement multiqueue support in Windows guest driver)
- Resolves: bz#1098876
  ([virtio-win][netkvm]netkvm driver can not be installed on win8-64 guests)
- Solves: bz#1100308
  ([NetKVM] Race condition in handling device stop)
- Solves: bz#1103100
  ([virtio-win][netkvm]netkvm driver can not be load in win2008 guest)
- Solves: bz#1106400
  ([whql][netkvm]NDISTest 6.5 - [2 Machine] - OffloadLSO failed)
- Solves: bz#1109027
  ([virtio-win][netkvm]Name field is empty when using netsh command)
- Solves: bz#1110129
  ([virtio-win][scsi]scsi driver can not be installed automately via pnputil)
- Solves: bz#1111051
  ([virtio-win][netkvm]win7-32 guest bsod(8e) while performing long (several hours) netperf transfer with mq=on)
- Resolves: bz#1112712
  ([virtio-win][netkvm]win8.1 32bit BSOD when loading virtio-win-prewhql-0.1 driver & indirect_desc=off option of virtio-net-pci)
- Resolves: bz#1119966
  ([whql][netkvm][RHEL6]guests bsod (0xd1) when running job "NDISTest 6.5 - [1 Machine] - StandardizedKeywords")
- Solves: bz#1121338
  ([WHQL][netkvm]NDISTest 6.5 - 2 Machine - OffloadChecksum failed via bridge on hck)
- Solves: bz#1123288
  ([virtio-win][netkvm]BOSD occurs during guest reboot after disable nic when netserver running)
- Solves: bz#1125796
  ("Guest moved used index from 10122 to 10253" when reboot win2012R2 guest with 129 virtio-scsi target)
- Solves: bz#1126378
  ([virtio-win][vioscsi][rhel6]win2012 guest bsod(d1) when shutdown guest with multi virtio-scsi devices on the same scsi controller)
- Solves: bz#1136023
  ([NetKVM] Google patches broke debug compilation of NetKVM driver)
- Solves: bz#1136602
  ([whql][netkvm]Guest (64 bits Operating System) got BSOD (DRIVER_VERIFIER_DETECTED_VIOLATION) while run some jobs)
- Solves: bz#1136606
  ([whql][netkvm]guests bsod(7E) when running job "NDISTest 6.0 - [1 Machine] - 1c_FaultHandling")
- Solves: bz#1140447
  ([virtio-win][viorng]should use uniformed name for WDFCoinstallerXXX.dll)
- Solves: bz#1142737
  ([virtio-win][netkvm]interface status is '2', but expect status is '7' after set_link NIC off)
- Solves: bz#1147202
  ([virtio-win][WHQL][netkvm]Job named by InvalidPackets induce win81-32/64 to hang up.)
- Solves: bz#1147203
  ([virtio-win][whql][netkvm]win2k8-64 bsod(7e) when run job "Ethernet - NDISTest 6.0")
- Solves: bz#1147239
  (NetKVM with 2012R2 fails the HCK tests)
- Solves: bz#1154419
  (NetKVM fails HCK test for 2008R2, single CPU)
- Solves: bz#1154420
  (ParaNdis6_SendNetBufferList should dispatch each net buffer to a separate queue)
- Solves: bz#1154435
  ([NetKVM] Incorrect message id assignment and queue allocation)
- Solves: bz#1155891
  ([whql][netkvm]Job MPE failed while job was running on win2008R2 because of bsod (0A) on build 93 - 4 vcpus)
- Solves: bz#1155910
  ([whql][netkvm]Job MPE failed while job was running on win2008R2 because of bsod (D1) on build 93 - 1 vcpus)
- Resolves: bz#1156259
  (Win7-64 guest BSOD(0x000000A0) when doing s4)
- Solves: bz#1157241
  ([NetKVM] Uninitialized reserved field in procNumber structure)
- Solves: bz#1159732
  ([virtio-win][vioscsi]guest shutdown instead of S3/S4 while doing S3/S4 in guest)
- Resolves: bz#1159754
  ([virtio-win][netkvm]Nic device doesn't work when guest is running in IRQ mode)
- Solves: bz#1167539
  (win8.1.32 guest BSOD with error ' MEMORY_MANAGEMENT)
- Solves: bz#1167614
  (win8.1.32 guest BSOD with error 'DRIVER_IRQL_NOT_LESS_OR_EQUAL' (netkvm.sys))
- Solves: bz#1168119
  ([virtio-win][netkvm]win8.1.64 guest BSOD with error 'DRIVER_IRQL_NOT_LESS_OR_EQUAL' (netkvm.sys) after first reboot during os installation on AMD host)
- Solves: bz#1168483
  ([virtio-win][netkvm]guest lost ip when change MTU between 500 and 575 via device manage)
- Solves: bz#1168784
  ([virtio-win]win2012r2 guest shows black screen with error code "0x0000005c" after migration and reboot)
- Solves: bz#1169673
  ([virtio-win][netkvm]qemu quit with "qemu-kvm: Guest moved used index from 0 to 257" when set MaxRxBuffers to 512/1024 in guest)
- Solves: bz#1169718
  (CVE-2015-3215 [NetKVM] Malformed packet can cause BSOD [rhel-7.2])
- Solves: bz#1170106
  (RFE: [virtio-win][qxl-win] Add windows 2008R2 QXL to the .vfd)
- Solves: bz#1172920
  ([virtio-win][vioser]winxp guest bsod with D1 code when shutdown guest after hotunplug/hotplug serial port and serial pci)
- Solves: bz#1173323
  (iperf stalls the NetKVM driver)
- Solves: bz#1177063
  ([virtio-win][balloon]guest can't s3/s4 correctly if disable guest-stats-polling while balloon service running)
- Solves: bz#1183423
  (Change the copyright on all the Windows drivers to "2015" in virtio-win-prewhql build)
- Solves: bz#1184430
  (enable event index feature in Windows virtio-blk driver)
- Resolves: bz#1184818
  (guest BSOD when reboot guest after enable qxl driver verifier)
- Solves: bz#1188790
  (NetKVM driver crashed on pausing in MPE test)
- Solves: bz#1190968
  ([whql][netkvm][mq]job "NDISTest 6.0 - [1 Machine] - 1c_Mini6RSSOids" last for hours and never stop w/ 4 queues)
- Solves: bz#1191836
  ([whql][netkvm][mq]job "NDISTest 6.5 - [2 Machine] - GlitchFreeDevice" failed due to "not received the expected number of packets" w/ 4 queues)
- Solves: bz#1195487
  (Windows guest performing out-of-bounds accesses on virtio device)
- Resolves: bz#1195920
  (Windows 2012 R2 using virtio-scsi driver with Direct LUNs causes BSODs)
- Solves: bz#1210208
  (CVE 2015-3215 [NetKVM] Malformed packet can cause BSOD [rhel-7.2])
- Resolves: bz#1212392
  (need to do extra Refresh work when initiate virtio-blk disk while boot guest with OVMF)
- Solves: bz#1217642
  (QXL XDDM is not shipped on the virtio-win ISO)
- Resolves: bz#1217644
  (use hardlinks for .iso and /usr/share/virtio-win/drivers)
- Solves: bz#1217799
  (Distribute *.oem, LICENSE, COPYING in -prewhql build)
- Resolves: bz#1218449
  (Ship qemuserial.cat on the iso)
- Solves: bz#1218937
  (QEMU Guest Agent VSS Provider is not started after guest tools install)
- Solves: bz#1227164
  (viostor/vioscsi is not digital signed by Redhat)
- Resolves: bz#1228967
  ([virtio-win][whql][viostor]job "Flush Test" failed on all guests with build 105)

* Mon Apr 13 2015 Jeff E. Nelson <jen@redhat.com> - 1.7.4-1
- Correct NVR of virtio-win-prewhql-build

- Resolves: bz#1183423 [rhel-7.2.0]
  (Change the copyright on all the Windows drivers to "2015" in virtio-win-preqhql build)
- Resolves: bz#1195920 [rhel-7.2.0]
  (Windows 2012 R2 using virtio-scsi-driver with Direct LUNs causes BSODs)
- Resolves: bz#1210208 [rhel-7.2.0]
  ([NetKVM] Malformed packet can cause BSOD)

* Fri Apr 10 2015 Jeff E. Nelson <jen@redhat.com> - 1.7.4-1
- Resolves: bz#1183423 [rhel-7.2.0]
  (Change the copyright on all the Windows drivers to "2015" in virtio-win-preqhql build)
- Resolves: bz#1195920 [rhel-7.2.0]
  (Windows 2012 R2 using virtio-scsi-driver with Direct LUNs causes BSODs)
- Resolves: bz#1210208 [rhel-7.2.0]
  ([NetKVM] Malformed packet can cause BSOD)

* Fri Jan  9 2015 Mike Bonnet <mikeb@redhat.com> - 1.7.3-1
- Update drivers and guest-agent installers
- Resolves: rhbz#1178458

* Fri Sep 19 2014 Mike Bonnet <mikeb@redhat.com> - 1.7.2-1
- Update drivers and guest-agent installers
- Resolves: rhbz#1047937

* Wed May 28 2014 Mike Bonnet <mikeb@redhat.com> - 1.7.1-1
- Update drivers and guest-agent installers
- Resolves: rhbz#1102235

* Sat Apr  5 2014 Mike Bonnet <mikeb@redhat.com> - 1.7.0-1
- Update serial drivers and guest-agent installers
- Resolves: rhbz#1025122

* Thu Feb 27 2014 Mike Bonnet <mikeb@redhat.com> - 1.6.8-5
- Update guest-agent installers
- Resolves: rhbz#827609

* Wed Jan 22 2014 Mike Bonnet <mikeb@redhat.com> - 1.6.8-4
- Re-update guest-agent installers

* Fri Jan 17 2014 Mike Bonnet <mikeb@redhat.com> - 1.6.8-3
- Update guest-agent installers

* Thu Jan 16 2014 Mike Bonnet <mikeb@redhat.com> - 1.6.8-2
- Add new drivers to the .vfds and .iso

* Wed Jan 15 2014 Mike Bonnet <mikeb@redhat.com> - 1.6.8-1
- Refresh the scsi driver

* Wed Dec  4 2013 Mike Bonnet <mikeb@redhat.com> - 1.6.7-3
- Fix the serial driver for Windows 2012

* Tue Oct 29 2013 Mike Bonnet <mikeb@redhat.com> - 1.6.7-2
- Remove netkvmco.dll from the floppy images to save space
- Related: rhbz#1018649

* Tue Oct 29 2013 Mike Bonnet <mikeb@redhat.com> - 1.6.7-1
- Update to the latest version of the drivers
- Add qemu-ga installers to the .iso
- Resolves: rhbz#1018649 rhbz#1018652 rhbz#908609

* Thu Aug 15 2013 Jay Greguske <jgregusk@redhat.com> 1.6.6-1
- Resolves: 968050

* Thu Jul 11 2013 Jay Greguske <jgregusk@redhat.com> 1.6.5-6
- Resolves: 983500 (CVE-2013-2231)

* Fri Jun 28 2013 Jay Greguske <jgregusk@redhat.com> 1.6.5-5
- Resolves: 979239

* Thu Jun 27 2013 Jay Greguske <jgregusk@redhat.com> 1.6.5-4
- Resolves: 978648 978282 977686

* Wed Jun 26 2013 Jay Greguske <jgregusk@redhat.com> 1.6.5-3
- Use OS-specific cat files for each OS

* Tue Jun 25 2013 Jay Greguske <jgregusk@redhat.com> 1.6.5-2
- Use an uncorrupted amd64 cat file

* Mon Jun 24 2013 Jay Greguske <jgregusk@redhat.com> 1.6.5-1
- Resolves 976310

* Mon Apr 29 2013 Jay Greguske <jgregusk@redhat.com> 1.6.4-1
- Resolves 956228

* Wed Feb 6 2013 Jay Greguske <jgregusk@redhat.com> 1.6.3-3
- added further fixed txtsetup.oem

* Wed Feb 6 2013 Jay Greguske <jgregusk@redhat.com> 1.6.3-2
- add fixed txtsetup.oem
- added win2k8r2 netkvm drivers

* Wed Feb 6 2013 Jay Greguske <jgregusk@redhat.com> 1.6.3-1
- Reorganize the VFDs to be 32/64 bit
- Fix 1009 balloon coinstallers being resigned
- Resolves: 908163, 891640

* Tue Feb 5 2013 Jay Greguske <jgregusk@redhat.com> 1.6.2-2
- Fix 1009 coinstallers being resigned
- Resolves: 891640

* Wed Jan 30 2013 Jay Greguske <jgregusk@redhat.com> 1.6.2-1
- Split up the VFD
- Resolves: 905011

* Tue Jan 29 2013 Jay Greguske <jgregusk@redhat.com> 1.6.1-2
- Remove vioser-test.pdbs
- Resolves: 838915

* Thu Jan 24 2013 Jay Greguske <jgregusk@redhat.com> 1.6.1-1
- Added drivers from submissions 1556359, 1557005, 1557012,
  1557004, 1557008, 1555597, 1552544, 1551826, 1549074,
  1546707
- Enabled Win8/2012 platforms
- Updated txtsetup.oem for Windows 2003
- Resolves: 902977, 857832, 803633, 880569, 836915,
  838021, 714908, 750421, 760022, 768795, 782268, 790305,
  797030, 797032, 797695, 799864, 800247, 800716, 801238,
  805423, 807967, 814684, 814896, 815295, 816452, 819412,
  824814, 827000, 828275, 831570, 833659, 833671, 834174,
  834175, 834179, 834679, 836474, 837321, 837758, 838002,
  838005, 838008, 839143, 839853, 840911, 841169, 841544,
  842961, 843325, 855826, 858551, 859882, 864841, 873128,
  873960, 873971, 875155, 876033, 876061, 876397, 876504,
  877333, 878291, 879143, 879178
- add the Windows guest agent and supporting .dlls to the .iso
  Resolves: 902977

* Wed Oct 31 2012 Jay Greguske <jgregusk@redhat.com> 1.6.0-1
- Added QXL drivers from submission 1534828
- Resolves: 871679

* Fri Aug 17 2012 Jay Greguske <jgregusk@redhat.com> 1.5.4-1
- Increased VFD size to 2.88M
- Resolves: 760022

* Fri Jul 6 2012 Jay Greguske <jgregusk@redhat.com> 1.5.3-1
- Updated drivers for vio-serial
- Resolved: 833659

* Tue May 29 2012 Jay Greguske <jgregusk@redhat.com> 1.5.2-1
- Fixed Windows XP block drivers

* Wed May 16 2012 Jay Greguske <jgregusk@redhat.com> 1.5.1-1
- Updated drivers for RHEL 6.3
- Resolved: 677219, 695053, 713643, 730877, 744729, 744730,
            751952, 752743, 753723, 759361, 760022, 769495,
            770499, 771390, 799178, 799182, 799190, 799248,
            799264, 808322, 808654, 810694, 811161

* Thu Oct  6 2011 Mike Bonnet <mikeb@redhat.com> - 1.4.0-1
- Updated drivers for RHEL 6.2

* Wed Aug 10 2011 Jay Greguske <jgregusk@redhat.com> - 1.3.3-0
- Removed xp/amd64 directories and drivers since we do not
  support that platform. (rhbz#728457)

* Fri Aug  5 2011 Michael Bonnet <mikeb@redhat.com> - 1.3.2-2
- fix the directory structure of the sources zip

* Thu Aug  4 2011 Mike Bonnet <mikeb@redhat.com> - 1.3.2-1
- update viostor.cat (rhbz#727799)

* Fri Jul 29 2011 Jay Greguske <jgregusk@redhat.com> 1.3.1-1
- Added new vioserial drivers (rhbz#721355)
- prewhql build: 0.1-13

* Tue Jul 26 2011 Jay Greguske <jgregusk@redhat.com> 1.3.0-1
- Added new vioserial drivers (rhbz#720540, rhbz#702258)
- prewhql build: 0.1-12
- included 00-ms-cross-cert.patch for the sake of completeness

* Tue Apr 26 2011 Jay Greguske <jgregusk@redhat.com> 1.2.0-1
- Fix 2k8-32 drivers

* Mon Apr 25 2011 Jay Greguske <jgregusk@redhat.com> 1.2.0-0
- Added viostor, vioserial and balloon drivers for 6.1 (rhbz#699570)

* Wed Mar 30 2011 Jay Greguske <jgregusk@redhat.com> 1.1.16-4
- remove hypercall drivers included in error
- add vioserial and balloon which were excluded in error

* Thu Mar 24 2011 Jay Greguske <jgregusk@redhat.com> 1.1.16-3
- fix viostor 2k8-64 driver direct from MS this time (rhbz#681958)

* Wed Mar 23 2011 Jay Greguske <jgregusk@redhat.com> - 1.1.16-2
- Sources now a zip rather than tarball
- fix viostor 2k8-64 driver (rhbz#681958)
- Removed .git in sources zip (rhbz#671187)

* Thu Feb 10 2011 Jay Greguske <jgregusk@redhat.com> - 1.1.16-1
- Fixed drivers zip (viostor, balloon and vioserial)

* Fri Jul 2 2010 Jay Greguske <jgregusk@redhat.com> - 1.1.16-0
- RHEL 6 rebuild with new drivers

* Thu May 13 2010 Dennis Gregorovic <dgregor@redhat.com> - 1.0.0-8.1.41879
- Bump for rebuild

* Mon Jan 18 2010 Jay Greguske <jgregusk@redhat.com> - 1.0.0-8.41879
- Updated drivers from sm17 tags

* Tue Nov 17 2009 Jay Greguske <jgregusk@redhat.com> - 1.0.0-7.39539
- Packages built with the rhevm-2.1 branch
- included installer fixes

* Mon Nov 16 2009 Jay Greguske <jgregusk@redhat.com> - 1.0.0-6.37540
- license file is in .txt format
- included fix to installers so the correct block drivers are used

* Wed Nov  4 2009 Jay Greguske <jgregusk@redhat.com> - 1.0.0-5.37540
- Added new license documentation

* Tue Nov  3 2009 Jay Greguske <jgregusk@redhat.com> - 1.0.0-4.37540
- Added dual-signed x64 2008/2008r2 net drivers

* Thu Jun 18 2009 Jay Greguske <jgregusk@redhat.com> - 1.0.0-2.31351
- Fixed licensing issue in source tarball

* Wed Jun 17 2009 Mike Bonnet <mikeb@redhat.com> - 1.0.0-1.31351
- rebuild from the latest upstream sources

* Thu May  7 2009 Mike Bonnet <mikeb@redhat.com> - 1.0.0-1.28503
- Initial build
