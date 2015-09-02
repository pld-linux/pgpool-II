#
# TODO
# - logrotate script
# - libpcp devel subpackage?
#
%bcond_without	openssl	# build without SSL support
%bcond_without	pam	# don't build with pam support
#
%define		relname	pgpool
#
Summary:	Pgpool - a connection pooling/replication server for PostgreSQL
Summary(pl.UTF-8):	Pgpool - serwer puli połączeń i replikacji dla PostgreSQL-a
Name:		pgpool-II
Version:	3.4.2
Release:	0.1
License:	BSD
Group:		Applications/Databases
Source0:	http://www.pgpool.net/mediawiki/images/%{name}-%{version}.tar.gz
# Source0-md5:	a2872b2ff70b2530b324b3bab86d0eb3
Source1:	%{relname}.init
Source2:	%{relname}.monitrc
Source3:	%{relname}.sysconfig
Source4:	%{relname}.tmpfiles
Patch0:		%{name}-libs.patch
URL:		http://www.pgpool.net/
%{?with_openssl:BuildRequires:	openssl-devel}
%{?with_pam:BuildRequires:	pam-devel}
BuildRequires:	postgresql-devel
BuildRequires:	postgresql-static
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
%{?with_pam:Requires:	pam}
Requires:	rc-scripts >= 0.2.0
Provides:	group(pgpool)
Provides:	pgpool
Provides:	user(pgpool)
Obsoletes:	pgpool
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Pgpool is a connection pooling/replication server for PostgreSQL.
Pgpool runs between PostgreSQL's clients(front ends) and servers
(backends). A PostgreSQL client can connect to pgpool as if it were a
standard PostgreSQL server.

SSL support: %{?with_openssl:en}%{!?with_openssl:dis}abled

%description -l pl.UTF-8
Pgpool to serwer puli połączeń i replikacji dla PostgreSQL-a. Pgpool
działa pomięzy klientami a serwerami PostgreSQL, umożliwiając klientom
połaczenie się do pgool tak jakby to był serwer PostgreSQL.

Wsparcie SSL: w%{!?with_openssl:y}łączone

%package -n monit-rc-pgpool-II
Summary:	pgpool support for monit
Summary(pl.UTF-8):	Wsparcie pgpool dla monit
Group:		Applications/System
Requires:	%{name}
Requires:	monit
Obsoletes:	monit-rc-pgpool

%description -n monit-rc-pgpool-II
monitrc file for pgpool monitoring.

%description -n monit-rc-pgpool-II -l pl.UTF-8
Plik monitrc do monitorowania pgpool.

%prep
%setup -q
%patch0 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}

CFLAGS="%{rpmcflags}"
CXXFLAGS="%{rpmcflags}"
export CFLAGS CXXFLAGS

%configure \
	--bindir=%{_bindir} \
	%{?with_openssl:--with-openssl} \
	%{?with_pam:--with-pam} \
	--sysconfdir=%{_sysconfdir}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/{sysconfig,monit,pam.d},%{_varrun}/pgpool,%{systemdtmpfilesdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/pcp.conf{.sample,}
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/pgpool.conf{.sample,}
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/pool_hba.conf{.sample,}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{relname}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/monit/%{relname}.monitrc
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{relname}
install %{SOURCE4} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{relname}.conf
%if %{with pam}
install src/sample/pgpool.pam $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/pgpool
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -r -g 240 pgpool
%useradd -r -u 240 -d /usr/share/empty -s /bin/false -c "Pgpool User" -g pgpool pgpool

%post
/sbin/chkconfig --add %{relname}
%service %{relname} restart

%preun
if [ "$1" = "0" ]; then
	%service %{relname} stop
	/sbin/chkconfig --del %{relname}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove pgpool
	%groupremove pgpool
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog NEWS README TODO doc src/sample src/sql
%attr(755,root,root) %{_bindir}/pcp_*
%attr(755,root,root) %{_bindir}/pg*
%attr(755,root,root) %{_libdir}/libpcp.so.*
%attr(754,root,root) /etc/rc.d/init.d/%{relname}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pcp.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pgpool.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pool_hba.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{relname}
%{_mandir}/man8/pgpool.8*
%{_datadir}/%{name}
%{_includedir}/*
%dir %attr(775,root,pgpool) %{_varrun}/pgpool
%{systemdtmpfilesdir}/%{relname}.conf
%if %{with pam}
%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/pgpool
%endif

%files -n monit-rc-pgpool-II
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/monit/%{relname}.monitrc
