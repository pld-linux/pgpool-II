#
# TODO
#	- I think it shuld be daemon so rc-scripts support is needed 
#	(user pgpool?)
#
Summary:	Pgpool is a connection pooling/replication server for PostgreSQL.
Name:		pgpool
Version:	2.6.3
Release:	0.1
Epoch:		0
License:	BSD
Group:		Applications/Databases
Source0:	http://pgfoundry.org/frs/download.php/426/%{name}-%{version}.tar.gz
# Source0-md5	
URL:		http://pgfoundry.org/projects/pgpool/
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Pgpool is a connection pooling/replication server for PostgreSQL.

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
install pgpool.conf.sample $RPM_BUILD_ROOT%{_sysconfdir}/pgpool.conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README README.euc_jp TODO AUTHORS COPYING INSTALL
%attr(755,root,root) %{_bindir}/pgpool
%config(noreplace) %verify(not md5 mtime size)/pgpool.conf
