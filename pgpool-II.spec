#
# TODO
#	- I think it shuld be daemon so rc-scripts support is needed 
#	(user pgpool?) init script must be fixed
#
%bcond_without	pam	# don't build with pam support
#
Summary:	Pgpool - a connection pooling/replication server for PostgreSQL
Summary(pl.UTF-8):	Pgpool - serwer puli połączeń i replikacji dla PostgreSQL-a
Name:		pgpool
Version:	3.4.1
Release:	0.1
License:	BSD
Group:		Applications/Databases
Source0:	http://pgfoundry.org/frs/download.php/1446/%{name}-%{version}.tar.gz
# Source0-md5:	1f876237923be8095ed6fb30885a416a
Source1:	%{name}.init
Source2:	%{name}.monitrc
Source3:	%{name}.sysconfig
URL:		http://pgfoundry.org/projects/pgpool/
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
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Pgpool is a connection pooling/replication server for PostgreSQL.
Pgpool runs between PostgreSQL's clients(front ends) and servers
(backends). A PostgreSQL client can connect to pgpool as if it
were a standard PostgreSQL server.

%description -l pl.UTF-8
Pgpool to serwer puli połączeń i replikacji dla PostgreSQL-a.

%package -n monit-rc-pgpool
Summary:	pgpool support for monit
Summary(pl.UTF-8):	wsparcie pgpool dla monit
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	monit

%description -n monit-rc-pgpool
monitrc file for pgpool monitoring.

%description -n monit-rc-pgpool -l pl.UTF-8
plik monitrc do monitorowania pgpool.

%prep
%setup -q
%build
CFLAGS="${CFLAGS:-%{rpmcflags}}" ; export CFLAGS
CXXFLAGS="${CXXFLAGS:-%{rpmcflags}}" ; export CXXFLAGS

%configure \
	--bindir %{_bindir} \
	%{?with_pam:--with-pam} \
	--sysconfdir=%{_sysconfdir}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/{sysconfig,logrotate.d,monit,pam.d} \
	$RPM_BUILD_ROOT%{_initrddir} \
        $RPM_BUILD_ROOT%{_sbindir} 

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
install pgpool $RPM_BUILD_ROOT%{_bindir}/
install pgpool.conf.sample   $RPM_BUILD_ROOT%{_sysconfdir}/pgpool.conf
install pool_hba.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/pool_hba.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/monit/%{name}.monitrc
install %{SOURCE3} $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/%{name}
%if %{with pam}
install pgpool.pam $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/pgpool
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -r -g 240 %{name}
%useradd -r -u 240 -d /usr/share/empty -s /bin/false -c "Pgpool User" -g %{name} %{name}

%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove %{name}
	%groupremove %{name}
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog NEWS README TODO pgpool.conf.sample pool_hba.conf.sample
%lang(ja) %doc README.euc_jp
%attr(755,root,root) %{_bindir}/pgpool
%attr(754,root,root) /etc/rc.d/init.d/pgpool
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pgpool.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pool_hba.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/sysconfig/%{name}
%{_mandir}/man8/pgpool.8*
%if %{with pam}
%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/%{name}
%endif

%files -n monit-rc-pgpool
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/monit/%{name}.monitrc
