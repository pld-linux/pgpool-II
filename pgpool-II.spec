#
# TODO
# - logrotate script
# - libpcp devel subpackage?
#
%bcond_without	pam	# don't build with pam support
#
%define		relname	pgpool
#
Summary:	Pgpool - a connection pooling/replication server for PostgreSQL
Summary(pl.UTF-8):	Pgpool - serwer puli połączeń i replikacji dla PostgreSQL-a
Name:		pgpool-II
Version:	2.2.2
Release:	1
License:	BSD
Group:		Applications/Databases
Source0:	http://pgfoundry.org/frs/download.php/2191/%{name}-%{version}.tar.gz
# Source0-md5:	6f14514ed4ed5368ad3ab7e2d4c5136b
Source1:	%{relname}.init
Source2:	%{relname}.monitrc
Source3:	%{relname}.sysconfig
URL:		http://pgpool.projects.postgresql.org/
BuildRequires:	postgresql-devel
%{?with_pam:BuildRequires: pam-devel}
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
%{?with_pam:Requires: pam}
Requires:	rc-scripts >= 0.2.0
Provides:	group(pgpool)
Provides:	user(pgpool)
Provides:	pgpool
Obsoletes:	pgpool
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Pgpool is a connection pooling/replication server for PostgreSQL.
Pgpool runs between PostgreSQL's clients(front ends) and servers
(backends). A PostgreSQL client can connect to pgpool as if it were a
standard PostgreSQL server.

%description -l pl.UTF-8
Pgpool to serwer puli połączeń i replikacji dla PostgreSQL-a.

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

%build
CFLAGS="%{rpmcflags}"
CXXFLAGS="%{rpmcflags}"
export CFLAGS CXXFLAGS

%configure \
	--bindir=%{_bindir} \
	%{?with_pam:--with-pam} \
	--sysconfdir=%{_sysconfdir}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/{sysconfig,monit,pam.d}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/pcp.conf{.sample,}
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/pgpool.conf{.sample,}
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/pool_hba.conf{.sample,}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{relname}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/monit/%{relname}.monitrc
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{relname}
%if %{with pam}
install sample/pgpool.pam $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/pgpool
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
%doc AUTHORS COPYING ChangeLog NEWS TODO doc sample sql
%lang(ja) %doc README.euc_jp
%attr(755,root,root) %{_bindir}/pcp_*
%attr(755,root,root) %{_bindir}/pg*
%attr(755,root,root) %{_libdir}/libpcp.so.*
%attr(754,root,root) /etc/rc.d/init.d/%{relname}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pcp.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pgpool.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pool_hba.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{relname}
%{_mandir}/man8/pgpool.8*
%if %{with pam}
%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/pgpool
%endif

%files -n monit-rc-pgpool-II
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/monit/%{relname}.monitrc
