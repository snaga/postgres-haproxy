%define haproxy_user    haproxy
%define haproxy_uid     188
%define haproxy_group   haproxy
%define haproxy_gid     188
%define haproxy_home    %{_localstatedir}/lib/haproxy
%define haproxy_confdir %{_sysconfdir}/haproxy
%define haproxy_datadir %{_datadir}/haproxy

Name: haproxy
Summary: HAProxy is a TCP/HTTP reverse proxy for high availability environments
Version: 1.5.11
Release: 1%{?dist}

Group: System Environment/Daemons
License: GPLv2+

URL: http://www.haproxy.org/
Source0: http://www.haproxy.org/download/1.5/src/haproxy-%{version}.tar.gz
Source1: haproxy.init
Source2: haproxy.cfg
Source3: haproxy.logrotate
Source4: halog.1

Patch0: halog-unused-variables.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: pcre-devel
BuildRequires: zlib-devel
BuildRequires: openssl-devel

Requires: pcre
Requires: openssl
Requires: setup >= 2.8.14-14

Requires(pre): %{_sbindir}/groupadd
Requires(pre): %{_sbindir}/useradd
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(postun): /sbin/service

%description
HAProxy is a TCP/HTTP reverse proxy which is particularly suited for high
availability environments. Indeed, it can:
 - route HTTP requests depending on statically assigned cookies
 - spread load among several servers while assuring server persistence
   through the use of HTTP cookies
 - switch to backup servers in the event a main one fails
 - accept connections to special ports dedicated to service monitoring
 - stop accepting connections without breaking existing ones
 - add, modify, and delete HTTP headers in both directions
 - block requests matching particular patterns
 - persists clients to the correct application server depending on
   application cookies
 - report detailed status as HTML pages to authenticated users from a URI
   intercepted from the application

%prep
%setup -q
%patch0 -p0

%build
%ifarch %ix86 x86_64
use_regparm="USE_REGPARM=1"
%endif

%{__make} %{?_smp_mflags} CPU="generic" TARGET="linux2628" USE_PCRE=1 USE_ZLIB=1 USE_OPENSSL=1 ${use_regparm} ADDINC="%{optflags}" USE_LINUX_TPROXY=1

pushd contrib/halog
%{__make} halog OPTIMIZE="%{optflags}"
popd

pushd contrib/iprange
%{__make} iprange OPTIMIZE="%{optflags}"
popd

%install
%{__rm} -rf %{buildroot}

%{__make} install-bin DESTDIR=%{buildroot} PREFIX=%{_prefix}
%{__make} install-man DESTDIR=%{buildroot} PREFIX=%{_prefix}

%{__install} -p -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{haproxy_confdir}/%{name}.cfg
%{__install} -p -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -p -D -m 0644 %{SOURCE4} %{buildroot}%{_mandir}/man1/halog.1
%{__install} -d -m 0755 %{buildroot}%{haproxy_home}
%{__install} -d -m 0755 %{buildroot}%{haproxy_datadir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -p -m 0755 ./contrib/halog/halog %{buildroot}%{_bindir}/halog
%{__install} -p -m 0755 ./contrib/iprange/iprange %{buildroot}%{_bindir}/iprange
%{__install} -p -m 0644 ./examples/errorfiles/* %{buildroot}%{haproxy_datadir}

%{__rm} -f %{buildroot}%{_sbindir}/haproxy-systemd-wrapper

for httpfile in $(find ./examples/errorfiles/ -type f)
do
    %{__install} -p -m 0644 $httpfile %{buildroot}%{haproxy_datadir}
done

for textfile in $(find ./ -type f -name '*.txt' -o -name README)
do
    %{__mv} $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    %{__rm} -f $textfile.old
done

%clean
%{__rm} -rf %{buildroot}

%pre
%{_sbindir}/groupadd -g %{haproxy_gid} -r %{haproxy_group} 2>/dev/null || :
%{_sbindir}/useradd -u %{haproxy_uid} -g %{haproxy_group} -d %{haproxy_home} -s /sbin/nologin -r %{haproxy_user} 2>/dev/null || :

%post
/sbin/chkconfig --add haproxy

%preun
if [ "$1" -eq 0 ]; then
    /sbin/service haproxy stop >/dev/null 2>&1
    /sbin/chkconfig --del haproxy
fi

%postun
if [ "$1" -ge 1 ]; then
    /sbin/service haproxy condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc doc/*
%doc examples/url-switching.cfg
%doc examples/acl-content-sw.cfg
%doc examples/content-sw-sample.cfg
%doc examples/cttproxy-src.cfg
%doc examples/haproxy.cfg
%doc examples/tarpit.cfg
%doc CHANGELOG LICENSE README
%dir %{haproxy_confdir}
%dir %{haproxy_datadir}
%{haproxy_datadir}/*
%config(noreplace) %{haproxy_confdir}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_initrddir}/%{name}
%{_sbindir}/%{name}
%{_bindir}/halog
%{_bindir}/iprange
%{_mandir}/man1/*
%attr(-,%{haproxy_user},%{haproxy_group}) %dir %{haproxy_home}

%changelog
* Wed Feb 11 2015 Satoshi Nagayasu <snaga@uptime.jp> - 1.5.11-1
- Rebase to upstream version 1.5.11

* Wed Sep 03 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.2-2
- Fix emote client denial of service vulnerability
  Resolves: rhbz#1136698

* Tue Jul 15 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.2-1
- Rebase to upstream version 1.5.2
  Resolves: rhbz#1081727

* Tue Jun 24 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.1-1
- Rebase to upstream version 1.5.1
  Resolves: rhbz#1081727

* Fri Jun 20 2014 Ryan O'Hara <rohara@redhat.com> - 1.5.0-1
- Rebase to upstream version 1.5.0
  Resolves: rhbz#1081727

* Fri May 30 2014 Ryan O'Hara <rohara@redhat.com> - 1.5-0.1.dev26
- Rebase to upstream version 1.5-dev26
  Resolves: rhbz#1081727

* Wed Jul 10 2013 Ryan O'Hara <rohara@redhat.com> - 1.4.24-2
- Drop supplementary groups after setuid/setgid calls.
  Resolves: rhbz#903303

* Wed Jul 10 2013 Ryan O'Hara <rohara@redhat.com> - 1.4.24-1
- Rebase to upstream version 1.4.24.
  Resolves: rhbz#947987
- Rewrite rules flaw can lead to arbitrary code execution (CVE-2013-1912).
  Resolves: rhbz#947701
- Fix possible crash when using negative header occurrences (CVE-2013-2175).
  Resolves: rhbz#974263
- Enable TPROXY support.
  Resolves: rhbz#921064

* Tue Oct 02 2012 Ryan O'Hara <rohara@redhat.com> - 1.4.22-3
- Use static uid/gid.
  Resolves: rhbz#846067

* Fri Sep 21 2012 Ryan O'Hara <rohara@redhat.com> - 1.4.22-2
- Bump release number.
  Resolves: rhbz#846067

* Thu Sep 20 2012 Ryan O'Hara <rohara@redhat.com> - 1.4.22-1
- Initial build.
  Resolves: rhbz#846067
