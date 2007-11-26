#
# TODO
#	- I think it shuld be daemon so rc-scripts support is needed 
#	(user pgpool?)
#
Summary:	Pgpool - a connection pooling/replication server for PostgreSQL
Summary(pl.UTF-8):	Pgpool - serwer puli połączeń i replikacji dla PostgreSQL-a
Name:		pgpool
Version:	3.4.1
Release:	1
License:	BSD
Group:		Applications/Databases
Source0:	http://pgfoundry.org/frs/download.php/1446/%{name}-%{version}.tar.gz
# Source0-md5:	1f876237923be8095ed6fb30885a416a
URL:		http://pgfoundry.org/projects/pgpool/
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Pgpool is a connection pooling/replication server for PostgreSQL.

%description -l pl.UTF-8
Pgpool to serwer puli połączeń i replikacji dla PostgreSQL-a.

%prep
%setup -q
%build
CFLAGS="${CFLAGS:-%{rpmcflags}}" ; export CFLAGS
CXXFLAGS="${CXXFLAGS:-%{rpmcflags}}" ; export CXXFLAGS

%configure \
	--bindir %{_bindir} \
	--sysconfdir=%{_sysconfdir}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
install pgpool $RPM_BUILD_ROOT%{_bindir}/
install pgpool.conf.sample   $RPM_BUILD_ROOT%{_sysconfdir}/pgpool.conf
install pool_hba.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/pool_hba.conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog NEWS README TODO
%lang(ja) %doc README.euc_jp
%attr(755,root,root) %{_bindir}/pgpool
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pgpool.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/pool_hba.conf
%{_mandir}/man8/pgpool.8*
