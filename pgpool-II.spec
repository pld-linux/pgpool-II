#
%bcond_without	openssl	# build without SSL support
%bcond_without	pam	# don't build with pam support
#
%define		relname	pgpool
#
Summary:	Pgpool - a connection pooling/replication server for PostgreSQL
Summary(pl.UTF-8):	Pgpool - serwer puli połączeń i replikacji dla PostgreSQL-a
Name:		pgpool-II
Version:	3.6.0
Release:	1
License:	BSD
Group:		Applications/Databases
Source0:	http://www.pgpool.net/mediawiki/images/%{name}-%{version}.tar.gz
# Source0-md5:	26f0e249067d150f01a9ca02804700eb
Source1:	%{relname}.init
Source2:	%{relname}.monitrc
Source3:	%{relname}.sysconfig
Source4:	%{relname}.tmpfiles
Source5:	%{relname}.service
Patch0:		config.patch
URL:		http://www.pgpool.net/
%{?with_openssl:BuildRequires:	openssl-devel}
%{?with_pam:BuildRequires:	pam-devel}
BuildRequires:	postgresql-devel
BuildRequires:	sed >= 4.0
BuildRequires:	rpmbuild(macros) >= 1.671
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	%{name}-libs = %{version}-%{release}
%{?with_pam:Requires:	pam}
Requires:	rc-scripts >= 0.2.0
Requires:	systemd-units >= 38
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

%package libs
Summary:	%{name} library
Summary:	Biblioteka %{name}
Group:		Libraries

%description libs
Pgpool libraries.

%description libs -l pl.UTF-8
Biblioteka %{name}.

%package devel
Summary:	Header files for %{name} library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki %{name}
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for %{name} library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki %{name}.

%package static
Summary:	Static %{name} library
Summary(pl.UTF-8):	Statyczna biblioteka %{name}
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static %{name} library.

%description static -l pl.UTF-8
Statyczna biblioteka %{name}.

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

install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/{sysconfig,monit,pam.d},%{_varrun}/pgpool,%{systemdtmpfilesdir},%{_mandir}/man{1,8},/var/log/pgpool,%{systemdunitdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/pcp.conf{.sample,}
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/pgpool.conf{.sample,}
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/pool_hba.conf{.sample,}
cp -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{relname}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/monit/%{relname}.monitrc
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{relname}
cp -p %{SOURCE4} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{relname}.conf
cp -p %{SOURCE5} $RPM_BUILD_ROOT%{systemdunitdir}/%{relname}.service
%if %{with pam}
cp -p src/sample/pgpool.pam $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/pgpool
%endif
cp -p doc/src/sgml/man1/*.1 $RPM_BUILD_ROOT%{_mandir}/man1/
cp -p doc/src/sgml/man8/*.8 $RPM_BUILD_ROOT%{_mandir}/man8/

touch $RPM_BUILD_ROOT%{_sysconfdir}/pool_passwd
%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/pgpool.conf.sample*

# hardlink identical binaries
for n in detach_node node_count node_info pool_status proc_count proc_info promote_node recovery_node stop_pgpool watchdog_info ; do
	diff -q $RPM_BUILD_ROOT%{_bindir}/pcp_$n $RPM_BUILD_ROOT%{_bindir}/pcp_attach_node
	%{__rm} $RPM_BUILD_ROOT%{_bindir}/pcp_$n
	ln $RPM_BUILD_ROOT%{_bindir}/pcp_attach_node $RPM_BUILD_ROOT%{_bindir}/pcp_$n
done

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -r -g 240 pgpool
%useradd -r -u 240 -d /usr/share/empty -s /bin/false -c "Pgpool User" -g pgpool pgpool

%post
/sbin/chkconfig --add %{relname}
%service %{relname} restart
%systemd_post %{relname}.service

%preun
if [ "$1" = "0" ]; then
	%service %{relname} stop
	/sbin/chkconfig --del %{relname}
fi
%systemd_preun %{relname}.service

%postun
if [ "$1" = "0" ]; then
	%userremove pgpool
	%groupremove pgpool
fi
%systemd_reload

%post libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog NEWS README TODO doc/src/sgml/html src/sample src/sql
%attr(755,root,root) %{_bindir}/pcp_*
%attr(755,root,root) %{_bindir}/pg*
%attr(755,root,root) %{_bindir}/watchdog_setup
%attr(754,root,root) /etc/rc.d/init.d/%{relname}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pcp.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pgpool.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pool_hba.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{relname}
%attr(640,pgpool,pgpool) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pool_passwd
%{_mandir}/man1/*.1*
%{_mandir}/man8/pgpool.8*
%{_datadir}/%{name}
%dir %attr(775,root,pgpool) %{_varrun}/pgpool
%{systemdtmpfilesdir}/%{relname}.conf
%{systemdunitdir}/%{relname}.service
%if %{with pam}
%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/pgpool
%endif
%attr(775,root,pgpool) /var/log/pgpool

%files libs
%defattr(644,root,root,755)
%ghost %attr(755,root,root) %{_libdir}/libpcp.so.1
%attr(755,root,root) %{_libdir}/libpcp.so.1.*

%files devel
%defattr(644,root,root,755)
%{_includedir}/*
%attr(755,root,root) %{_libdir}/libpcp.la
%attr(755,root,root) %{_libdir}/libpcp.so

%files static
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libpcp.a

%files -n monit-rc-pgpool-II
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/monit/%{relname}.monitrc
