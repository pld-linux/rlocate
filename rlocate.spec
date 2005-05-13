#
# TODO:
# - cleanups, fix build, test... everything...
# - device: /dev/rlocate
#
# Conditional build:
%bcond_without  dist_kernel     # allow non-distribution kernel
%bcond_without  kernel          # don't build kernel modules
%bcond_without  smp             # don't build SMP module
%bcond_without  userspace       # don't build userspace module
%bcond_with     verbose         # verbose build (V=1)
#
Summary:	Finds files on a system via a central database
Summary(pl):	Szukanie plików w systemie poprzez centraln± bazê danych
Name:		rlocate
Version:	0.2.2
%define         _rel 0.1
Release:	%{_rel}
License:	GPL
Group:		Base
Source0:	http://dl.sourceforge.net/rlocate/%{name}-%{version}.tar.gz
# Source0-md5:	c6147ff49c3270b542ae431b7e81394f
#Source1:	%{name}.cron
#Source2:	%{name}-updatedb.conf
#Patch0:		%{name}-segfault.patch
#Patch1:		%{name}-manpage.patch
#Patch2:		%{name}-wht.patch
#Patch3:		%{name}-LOCATE_PATH.patch
#Patch4:		%{name}-uchar.patch
#Patch5:		%{name}-can-2003-0848.patch
URL:		http://rlocate.sourceforge.net/
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build >= 2.6
%endif
BuildRequires:	rpmbuild(macros) >= 1.202
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(postun):	/usr/sbin/groupdel
Requires:	crondaemon
Provides:	group(rlocate)
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
rlocate to implementacja polecenia locate bêd±ca zawsze aktualna. Baza
danych u¿ywana przez oryginalne polecenie locate jest zwykle
uaktualniana raz dziennie, wiêc nowszych plików nie mo¿na znale¼æ w
ten sposób. Zachowanie rlocate jest takie samo jak slocate, ale
rlocate dodatkowo utrzymuje bazê danych ró¿nic uaktualnian± przy
tworzeniu ka¿dego nowego pliku. Jest to osi±gniête przy u¿yciu modu³u
j±dra i demona rlocate. Modu³ j±dra mo¿na skompilowaæ tylko na j±drach
Linuksa 2.6.

%package -n kernel-misc-%{name}
Summary:	rlocate Linux module
Summary(pl):	Modu³ rlocate dla Linuksa
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
Ten pakiet zawiera modu³ rlocate dla j±dra Linuksa.

%package -n kernel-smp-misc-%{name}
Summary:	rlocate Linux SMP module
Summary(pl):	Modu³ rlocate dla Linuksa SMP
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
Ten pakiet zawiera modu³ rlocate dla j±dra Linuksa SMP.

%prep
%setup -q
#%patch0 -p1
#%patch1 -p1
#%patch2 -p1
#%patch3 -p1
#%patch4 -p1
#%patch5 -p1

%build
%if %{with userspace}
%configure
%{__make} -C rlocate-daemon
%{__make} -C doc
%endif

%if %{with kernel}
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

%if %{with userspace}
%{__make} -C rlocate-daemon install \
        DESTDIR=$RPM_BUILD_ROOT
%{__make} -C doc install \
        DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,/etc/cron.daily,/var/lib/rlocate}

#install rlocate $RPM_BUILD_ROOT%{_bindir}
ln -sf rlocate $RPM_BUILD_ROOT%{_bindir}/locate
ln -sf rlocate $RPM_BUILD_ROOT%{_bindir}/updatedb

#install doc/rlocate.1.linux $RPM_BUILD_ROOT%{_mandir}/man1/rlocate.1
#install doc/updatedb.1 $RPM_BUILD_ROOT%{_mandir}/man1/updatedb.1
#echo ".so rlocate.1" > $RPM_BUILD_ROOT%{_mandir}/man1/locate.1
#install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.daily/rlocate
#install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/updatedb.conf
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
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 37 rlocate

%post
if [ ! -f /var/lib/rlocate/rlocate.db ]; then
	echo 'Run "%{_bindir}/updatedb" if you want to make rlocate database immediately.'
fi

%postun
if [ "$1" = "0" ]; then
	%groupremove rlocate
fi

%if %{with kernel}
%files -n kernel-misc-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-misc-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(2755,root,slocate) %{_sbindir}/rlocated
%{_mandir}/man1/rlocate*
%{_mandir}/man1/updatedb.*

#doc AUTHORS ChangeLog README
#attr(2755,root,rlocate) %{_bindir}/rlocate
#attr(0755,root,root) %{_bindir}/locate
#attr(0755,root,root) %{_bindir}/updatedb
#attr(0750,root,root) /etc/cron.daily/rlocate
#attr(0640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/updatedb.conf
#dir %attr(750,root,rlocate) /var/lib/rlocate
#{_mandir}/man1/*
%endif
