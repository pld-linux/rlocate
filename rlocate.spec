# TODO
# - kernel module: doesn't build with Linux 3.x
# - device: installed with static major, module creates as dynamic => use udev
# - should provide something like virtual(locate), obsolete other implementations
# - conflicts: rlocate gid with slocate
# - pldize initscript
#
# Conditional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)

#
%define		_rel	0.1
Summary:	Finds files on a system via a central database
Summary(pl.UTF-8):	Szukanie plików w systemie poprzez centralną bazę danych
Name:		rlocate
Version:	0.5.6
Release:	%{_rel}
License:	GPL v2+
Group:		Base
Source0:	http://downloads.sourceforge.net/rlocate/%{name}-%{version}.tar.gz
# Source0-md5:	b834e2b1249fba9138bea29a030de46c
Patch0:		%{name}-build.patch
Patch1:		%{name}-open.patch
URL:		http://rlocate.sourceforge.net/
BuildRequires:	autoconf >= 2.50
BuildRequires:	automake >= 1:1.7.1
%if %{with kernel}
BuildRequires:	kernel-module-build >= 3:2.6
%endif
BuildRequires:	perl-base
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	crondaemon
Provides:	group(rlocate)
Conflicts:	slocate
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
rlocate is an implementation of the locate command that is always
up-to-date. The database that the original locate uses is usually
updated only once a day, so newer files cannot be located right away.
The behavior of rlocate is the same as slocate, but it also maintains
a diff database that gets updated whenever a new file is created. This
is accomplished with rlocate kernel module and daemon. The rlocate
kernel module can be compiled only with Linux 2.6 kernels.

%description -l pl.UTF-8
rlocate to implementacja polecenia locate będąca zawsze aktualna. Baza
danych używana przez oryginalne polecenie locate jest zwykle
uaktualniana raz dziennie, więc nowszych plików nie można znaleźć w
ten sposób. Zachowanie rlocate jest takie samo jak slocate, ale
rlocate dodatkowo utrzymuje bazę danych różnic uaktualnianą przy
tworzeniu każdego nowego pliku. Jest to osiągnięte przy użyciu modułu
jądra i demona rlocate. Moduł jądra można skompilować tylko na jądrach
Linuksa 2.6.

%package -n kernel-misc-%{name}
Summary:	rlocate Linux module
Summary(pl.UTF-8):	Moduł rlocate dla Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%requires_releq_kernel
Requires(postun):	%releq_kernel

%description -n kernel-misc-%{name}
This package contains rlocate Linux module.

%description -n kernel-misc-%{name} -l pl.UTF-8
Ten pakiet zawiera moduł rlocate dla jądra Linuksa.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%if %{with userspace}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--localstatedir=/var/lib

%{__make}
%endif

%if %{with kernel}
echo "EXTRA_CFLAGS:= -DRL_VERSION=\\\"%{version}\\\" -DRLOCATE_UPDATES" > src/rlocate-module/Makefile
echo "obj-m:= rlocate.o" >> src/rlocate-module/Makefile

%build_kernel_modules -m rlocate -C src/rlocate-module
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/dev,/etc/rc.d/init.d,%{_sysconfdir}/%{name}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cp -p contrib/rlocate.redhat $RPM_BUILD_ROOT/etc/rc.d/init.d/rlocate
cp -p debian/updatedb.conf $RPM_BUILD_ROOT%{_sysconfdir}
:> $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/module.cfg
%endif

%if %{with kernel}
%install_kernel_modules -m src/rlocate-module/rlocate -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 37 rlocate

%post
if [ ! -f /var/lib/rlocate/rlocate.db ]; then
	echo 'Run "%{_bindir}/updatedb" if you want to make rlocate database immediately.'
fi
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%groupremove rlocate
fi

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog README
%attr(700,root,root) %dir %{_sysconfdir}/%{name}
%attr(600,root,root) %ghost %{_sysconfdir}/%{name}/module.cfg
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/updatedb.conf
%attr(755,root,root) /etc/cron.daily/rlocate
%attr(754,root,root) /etc/rc.d/init.d/rlocate

%attr(2755,root,rlocate) %{_bindir}/rlocate
%attr(2755,root,rlocate) %{_bindir}/rlocate-checkpoint
%attr(755,root,root) %{_sbindir}/rlocated

# symlinks
%attr(755,root,root) %{_bindir}/updatedb
%attr(755,root,root) %{_bindir}/locate

%{_mandir}/man1/rlocate.1*
%{_mandir}/man1/rlocate-checkpoint.1*
%{_mandir}/man1/rlocated.1*
%{_mandir}/man1/updatedb.1*

# FIXME: use udev to get proper major
%attr(400,root,root) %dev(c,254,0) /dev/rlocate
%dir %attr(750,root,rlocate) /var/lib/rlocate
%endif

%if %{with kernel}
%files -n kernel-misc-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/rlocate.ko*
%endif
