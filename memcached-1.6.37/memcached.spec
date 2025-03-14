%bcond_with extstore
%bcond_with seccomp
%bcond_with sasl
%bcond_with sasl_pwdb
%bcond_with dtrace
%bcond_with 64bit
%bcond_without option_checking
%bcond_without coverage
%bcond_without docs

# Set with_systemd on distros that use it, so we can install the service
# file, otherwise the sysvinit script will be installed
%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7 || 0%{?suse_version} >= 1210
%global with_systemd 1
BuildRequires: systemd-units

# Disable some systemd safety features on OSes without a new enough systemd
# (new enough is systemd >= 233)
%if 0%{?fedora} < 26 || 0%{?rhel} > 0
%global safer_systemd 0
%else
%global safer_systemd 1
%endif

%else
%global with_systemd 0
%endif

Name:           memcached
Version:        1.6.37
Release:        1%{?dist}
Summary:        High Performance, Distributed Memory Object Cache

Group:          System Environment/Daemons
License:        BSD
URL:            https://memcached.org
Source0:        https://memcached.org/files/%{name}-%{version}.tar.gz
Source1:        memcached.sysconfig
Source2:        memcached.service
Source3:        memcached@.service
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libevent-devel
BuildRequires:  perl(Test::More)
BuildRequires:  /usr/bin/prove
Requires: initscripts
%if %{with_systemd}
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
%else
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig, /sbin/service
Requires(postun): /sbin/service
%endif

%description
memcached is a high-performance, distributed memory object caching
system, generic in nature, but intended for use in speeding up dynamic
web applications by alleviating database load.

%prep
%setup -q -n %{name}-%{version}


%build
%configure \
  %{?with_extstore:--enable-extstore} \
  %{?with_seccomp:--enable-seccomp} \
  %{?with_sasl:--enable-sasl} \
  %{?with_sasl_pwdb:--enable-pwdb} \
  %{?with_dtrace:--enable-dtrace} \
  %{?with_64bit:--enable-64bit} \
  %{!?with_option_checking:--disable-option-checking}
  %{!?with_coverage:--disable-coverage} \
  %{!?with_docs:--disable-docs}

make %{?_smp_mflags}


%check
make test


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# remove memcached-debug
rm -f %{buildroot}/%{_bindir}/%{name}-debug

# Perl script for monitoring memcached
install -Dp -m0755 scripts/memcached-tool %{buildroot}%{_bindir}/%{name}-tool

# Init script
%if %{with_systemd}
install -Dp -m0755 scripts/memcached.service %{buildroot}%{_unitdir}/%{name}.service
install -Dp -m0755 scripts/memcached@.service %{buildroot}%{_unitdir}/%{name}@.service

if [ %{safer_systemd} -gt 0 ]; then
    sed -e 's/^##safer##//g' -i %{buildroot}%{_unitdir}/%{name}.service %{buildroot}%{_unitdir}/%{name}@.service
else
    sed -e 's/^##safer##/#/g' -i %{buildroot}%{_unitdir}/%{name}.service %{buildroot}%{_unitdir}/%{name}@.service
fi
%else
install -Dp -m0755 scripts/memcached.sysv %{buildroot}%{_initrddir}/%{name}
%endif

# Default configs
install -Dp -m0644 scripts/memcached.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# pid directory
mkdir -p %{buildroot}/%{_localstatedir}/run/%{name}


%clean
rm -rf %{buildroot}


%post
if [ $1 -eq 1 ]; then
    # Initial install
%if %{with_systemd}
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%else
    /sbin/chkconfig --add %{name}
%endif
fi


%preun
if [ "$1" = 0 ] ; then
    # Removal, not upgrade
%if %{with_systemd}
    /bin/systemctl --no-reload disable %{name}.service > /dev/null 2>&1 || :
    /bin/systemctl --no-reload disable %{name}@\*.service > /dev/null 2>&1 || :
    /bin/systemctl stop %{name}.service > /dev/null 2>&1 || :
    /bin/systemctl stop %{name}@\*.service > /dev/null 2>&1 || :
%else
    /sbin/service %{name} stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del %{name}
%endif
fi

exit 0


%postun
%if %{with_systemd}
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%endif

# Don't auto-restart memcached on upgrade -- let user control when cache flushes
# if [ "$1" -ge 1 ]; then
#    # upgrade, not install
#    %if %{with_systemd}
#        /bin/systemctl try-restart %{name}.service
#        /bin/systemctl try-restart %{name}@\*.service
#    %else
#        /sbin/service %named condrestart 2>/dev/null || :
#    %endif
#fi

exit 0


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README.md doc/CONTRIBUTORS doc/*.txt
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}

%dir %attr(750,nobody,nobody) %{_localstatedir}/run/%{name}
%{_bindir}/%{name}-tool
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_includedir}/%{name}

%if %{with_systemd}
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%else
%{_initrddir}/%{name}
%endif

%changelog
* Wed Jul  5 2017 J. Grizzard <jg-github@lupine.org> - 1.4.39
- Add systemd-aware build
- Add both static and instanced versions of memcached unit files

* Mon Nov  2 2009 Dormando <dormando@rydia.net> - 1.4.3-1
- Fix autogen more.

* Sat Aug 29 2009 Dustin Sallings <dustin@spy.net> - 1.4.1-1
- Autogenerate the version number from tags.

* Wed Jul  4 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-5
- Use /var/run/memcached/ directory to hold PID file

* Sat May 12 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-4
- Remove tabs from spec file, rpmlint reports no more errors

* Thu May 10 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-3
- Enable build-time regression tests
- add dependency on initscripts
- remove memcached-debug (not needed in dist)
- above suggestions from Bernard Johnson

* Mon May  7 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-2
- Tidiness improvements suggested by Ruben Kerkhof in bugzilla #238994

* Fri May  4 2007 Paul Lindner <lindner@inuus.com> - 1.2.2-1
- Initial spec file created via rpmdev-newspec
