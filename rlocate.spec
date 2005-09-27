# TODO
# - device: /dev/rlocate (added to module package, but it should be probably in dev?)
# - conflicts: updatedb manual with slocate
# - conflicts: rlocate gid with slocate
# - it needs rlocated daemon?
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif
#
Summary:	Finds files on a system via a central database
Summary(pl):	Szukanie plik�w w systemie poprzez centraln� baz� danych
Name:		rlocate
Version:	0.3.3
%define		_rel	0.1
Release:	%{_rel}
License:	GPL
Group:		Base
Source0:    http://dl.sourceforge.net/rlocate/%{name}-%{version}.tar.gz
# Source0-md5:	ec08bea10ff51cb796280a61f9ab4ff2
Patch0:		%{name}-build.patch
URL:		http://rlocate.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build >= 2.6
%endif
BuildRequires:	libtool
BuildRequires:	perl-base
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(postun):	/usr/sbin/groupdel
Requires(post,preun):	/sbin/chkconfig
Requires:	crondaemon
Provides:	group(rlocate)
Conflicts:	slocate
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
rlocate is an implementation of the ``locate'' command that is always
up-to-date. The database that the original locate uses is usually
updated only once a day, so newer files cannot be located right away.
The behavior of rlocate is the same as slocate, but it also maintains
a diff database that gets updated whenever a new file is created. This
is accomplished with rlocate kernel module and daemon. The rlocate
kernel module can be compiled only with Linux 2.6 kernels.

%description -l pl
rlocate to implementacja polecenia locate b�d�ca zawsze aktualna. Baza
danych u�ywana przez oryginalne polecenie locate jest zwykle
uaktualniana raz dziennie, wi�c nowszych plik�w nie mo�na znale�� w
ten spos�b. Zachowanie rlocate jest takie samo jak slocate, ale
rlocate dodatkowo utrzymuje baz� danych r�nic uaktualnian� przy
tworzeniu ka�dego nowego pliku. Jest to osi�gni�te przy u�yciu modu�u
j�dra i demona rlocate. Modu� j�dra mo�na skompilowa� tylko na j�drach
Linuksa 2.6.

%package -n kernel-misc-%{name}
Summary:	rlocate Linux module
Summary(pl):	Modu� rlocate dla Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-misc-%{name}
This package contains rlocate Linux module.

%description -n kernel-misc-%{name} -l pl
Ten pakiet zawiera modu� rlocate dla j�dra Linuksa.

%package -n kernel-smp-misc-%{name}
Summary:	rlocate Linux SMP module
Summary(pl):	Modu� rlocate dla Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-misc-%{name}
This package contains rlocate Linux SMP module.

%description -n kernel-smp-misc-%{name} -l pl
Ten pakiet zawiera modu� rlocate dla j�dra Linuksa SMP.

%prep
%setup -q
%patch0 -p1

%build
%if %{with userspace}
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--localstatedir=/var/lib

%{__make}
%endif

%if %{with kernel}

%if %{without dist_kernel}
cat 2>&1 <<'EOF'
WARNING:
- CONFIG_SECURITY must be enabled in the kernel config,
- Capabilities must be built as a module or disabled in the kernel config,
for nondist kernel build to work.
EOF
%endif

# kernel module(s)
cd rlocate-module
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER

	echo "EXTRA_CFLAGS:= -DRL_VERSION=\\\"%{version}\\\" -DRLOCATE_UPDATES" > Makefile
	echo "obj-m:= rlocate.o" >> Makefile

	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}

	mv rlocate{,-$cfg}.ko
done
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -d $RPM_BUILD_ROOT/etc/cron.daily
install contrib/rlocate.redhat $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install rlocate.cron $RPM_BUILD_ROOT/etc/cron.daily/rlocate

%if %{with userspace}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/var/lib/rlocate,%{_sysconfdir}/%{name}}
install debian/updatedb.conf $RPM_BUILD_ROOT%{_sysconfdir}
> $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/module.cfg
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
cd rlocate-module
install rlocate-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/rlocate.ko
%if %{with smp} && %{with dist_kernel}
install rlocate-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/rlocate.ko
%endif
cd ..
install -d $RPM_BUILD_ROOT/dev
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

%postun
if [ "$1" = "0" ]; then
	%groupremove rlocate
else
if [ "$1" = "0" ]; then
        %service -q %{name} stop
        /sbin/chkconfig --del %{name}
fi

%if %{with kernel}
%files -n kernel-misc-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%dev(c,254,0) /dev/rlocate

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-misc-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%dev(c,254,0) /dev/rlocate
%endif
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(700,root,root) %dir %{_sysconfdir}/%{name}
%attr(0,root,root) %ghost %{_sysconfdir}/%{name}/module.cfg
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/updatedb.conf
%attr(755,root,root) /etc/cron.daily/rlocate

%attr(2755,root,rlocate) %{_bindir}/rlocate
%attr(2755,root,rlocate) %{_bindir}/rlocate-checkpoint
%attr(2755,root,rlocate) %{_sbindir}/rlocated

# symlinks
%{_bindir}/updatedb
%{_bindir}/locate

%{_mandir}/man1/rlocate*
%{_mandir}/man1/updatedb.*

%dir %attr(750,root,rlocate) /var/lib/rlocate
%endif

%attr(754,root,root) /etc/rc.d/init.d/%{name}
