#
# TODO:
# - cleanups, fix build, test... everything...
#

%bcond_without  dist_kernel     # allow non-distribution kernel
%bcond_without  kernel          # don't build kernel modules
%bcond_without  smp             # don't build SMP module
%bcond_without  userspace       # don't build userspace module
%bcond_with     verbose         # verbose build (V=1)

Summary:	Finds files on a system via a central database
Summary(es):	Localiza archivos en un sistema por medio del banco central de datos
Summary(pl):	Narz�dzie do odnajdywania plik�w w systemie poprzez specjaln� baz� danych
Summary(pt_BR):	Localiza arquivos em um sistema via um banco de dados central
Summary(ru):	����� ������ � �������� ������� ��� ������ ����������� ���� ������
Summary(uk):	����� ���̦� � �����צ� �����ͦ �� ��������� ���������ϧ ���� �����
Name:		rlocate
Version:	0.2.1
Release:	0.0.1
License:	GPL
Group:		Base
Source0:	http://dl.sourceforge.net/rlocate/%{name}-%{version}.tar.gz
# Source0-md5:	621bae5e9e4ad8f11e139e031692097b
#Source1:	%{name}.cron
#Source2:	%{name}-updatedb.conf
#Patch0:		%{name}-segfault.patch
#Patch1:		%{name}-manpage.patch
#Patch2:		%{name}-wht.patch
#Patch3:		%{name}-LOCATE_PATH.patch
#Patch4:		%{name}-uchar.patch
#Patch5:		%{name}-can-2003-0848.patch
URL:		http://rlocate.sourceforge.net/
BuildRequires:	rpmbuild(macros) >= 1.159
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(postun):	/usr/sbin/groupdel
Requires:	crondaemon
Provides:	group(rlocate)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Rlocate searches through a central database (updated nightly) for
files which match a given glob pattern. This allows you to quickly
find files anywhere on your system.

%description -l es
Localiza archivos en un sistema por medio del banco central de datos.

%description -l pl
Rlocate s�u�y do szybkiego poszukiwania plik�w poprzez specjaln� baz�
danych (aktualizowan� co noc). Umo�liwia tak�e szybkie odszukanie
pliku wed�ug podanego wzoru w postaci wyra�enia regularnego.

%description -l pt_BR
O rlocate localiza arquivos em um sistema via um banco de dados
central (Atualizado toda madrugada). Isto permite a voc� localizar
rapidamente arquivos em qualquer parte do seu sistema.

%description -l ru
Rlocate - ��� ������ locate � ���������� ������������� (��� ��
���������� ����� ������, ������� �� �� ����� �� ������ ����������
�������� �������). ��� � locate, rlocate ���������� ����� �
����������� ���� ������ (������� �����������, ��� �������, ��������)
������, ���������� ��������� �������.

%description -l uk
Rlocate - �� ���Ӧ� locate � ���������� ������Φ��� (���� �� �����դ
����� ���̦�, �˦ �� �� ������ � Ħ������� ���������� ������ϧ
�������). �� � locate, rlocate ��������� ����� � ��������Φ� ��ڦ
����� (��� �����Ѥ����, �� �������, ����ަ) ���̦�, �� צ���צ�����
�������� �������.

%package -n kernel-misc-%{name}
Summary:	Linux driver for %{name}
Summary(pl):	Sterownik dla Linuksa do %{name}
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-misc-%{name}
This is driver for %{name} for Linux.

This package contains Linux module.

%description -n kernel-misc-%{name} -l pl
Sterownik dla Linuksa do %{name}.

Ten pakiet zawiera modu� j�dra Linuksa.

%package -n kernel-smp-misc-%{name}
Summary:	Linux SMP driver for %{name}
Summary(pl):	Sterownik dla Linuksa SMP do %{name}
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-misc-%{name}
This is driver for %{name} for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-misc-%{name} -l pl
Sterownik dla Linuksa do %{name}.

Ten pakiet zawiera modu� j�dra Linuksa SMP.

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
make -C rlocate-daemon
make -C doc
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
	echo "obj-m := rlocate.o" >> Makefile

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


install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,/etc/cron.daily,/var/lib/rlocate}

#install rlocate $RPM_BUILD_ROOT%{_bindir}
ln -sf rlocate $RPM_BUILD_ROOT%{_bindir}/locate
ln -sf rlocate $RPM_BUILD_ROOT%{_bindir}/updatedb

#install doc/rlocate.1.linux $RPM_BUILD_ROOT%{_mandir}/man1/rlocate.1
#install doc/updatedb.1 $RPM_BUILD_ROOT%{_mandir}/man1/updatedb.1
#echo ".so rlocate.1" > $RPM_BUILD_ROOT%{_mandir}/man1/locate.1
#install %{SOURCE1} $RPM_BUILD_ROOT/etc/cron.daily/rlocate
#install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/updatedb.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid rlocate`" ]; then
	if [ "`/usr/bin/getgid rlocate`" != "21" ]; then
		echo "Error: group rlocate doesn't have gid=21. Correct this before installing rlocate." 1>&2
		exit 1
	fi
else
	echo "Adding group rlocate GID=21."
	/usr/sbin/groupadd -g 21 rlocate 1>&2
fi

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


%files
%defattr(644,root,root,755)
#doc AUTHORS ChangeLog README
#attr(2755,root,rlocate) %{_bindir}/rlocate
#attr(0755,root,root) %{_bindir}/locate
#attr(0755,root,root) %{_bindir}/updatedb
#attr(0750,root,root) /etc/cron.daily/rlocate
#attr(0640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/updatedb.conf
#dir %attr(750,root,rlocate) /var/lib/rlocate
#{_mandir}/man1/*
