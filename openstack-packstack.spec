%define milestone .0rc2
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%{!?upstream_version:   %global upstream_version         %{version}%{milestone}}


# openstack-packstack ----------------------------------------------------------

Name:           openstack-packstack
Version:        8.0.0
Release:        0.8%{milestone}%{?dist}
Summary:        Openstack Install Utility

Group:          Applications/System
License:        ASL 2.0 and GPLv2
URL:            https://github.com/openstack/packstack
Source0:        http://tarballs.openstack.org/packstack/packstack-%{upstream_version}.tar.gz

#
# patches_base=8.0.0.0rc2
#
Patch0001: 0001-Fix-gate-Tempest-setup-and-repositories.patch
Patch0002: 0002-Workaround-for-dev-kvm-permissions-issues.patch
Patch0003: 0003-Packstack-should-not-specify-release-when-installint.patch
Patch0004: 0004-Ensure-aodh-and-horizon-templates-do-not-overwrite-p.patch

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools

Requires:       openssh-clients
Requires:       python-netaddr
Requires:       openstack-packstack-puppet == %{version}-%{release}
Requires:       openstack-puppet-modules >= 2014.2.10
Obsoletes:      packstack-modules-puppet
Requires:       python-setuptools
Requires:       PyYAML
Requires:       python-docutils
Requires:       pyOpenSSL

%description
Packstack is a utility that uses Puppet modules to install OpenStack. Packstack
can be used to deploy various parts of OpenStack on multiple pre installed
servers over ssh.


# openstack-packstack-puppet ---------------------------------------------------

%package puppet
Summary:        Packstack Puppet module
Group:          Development/Libraries

%description puppet
Puppet module used by Packstack to install OpenStack


# openstack-packstack-doc ------------------------------------------------------

%if 0%{?with_doc}
%package doc
Summary:          Documentation for Packstack
Group:            Documentation

%if 0%{?rhel} == 6
BuildRequires:  python-sphinx10
%else
BuildRequires:  python-sphinx
%endif

%description doc
This package contains documentation files for Packstack.
%endif


# prep -------------------------------------------------------------------------

%prep
%setup -n packstack-%{upstream_version}

%patch0001 -p1
%patch0002 -p1
%patch0003 -p1
%patch0004 -p1

# Sanitizing a lot of the files in the puppet modules
find packstack/puppet/modules \( -name .fixtures.yml -o -name .gemfile -o -name ".travis.yml" -o -name .rspec \) -exec rm {} +
find packstack/puppet/modules \( -name "*.py" -o -name "*.rb" -o -name "*.pl" \) -exec sed -i '/^#!/{d;q}' {} + -exec chmod -x {} +
find packstack/puppet/modules \( -name "*.sh" \) -exec sed -i 's/^#!.*/#!\/bin\/bash/g' {} + -exec chmod +x {} +
find packstack/puppet/modules -name site.pp -size 0 -exec rm {} +
find packstack/puppet/modules \( -name spec -o -name ext \) | xargs rm -rf

# Moving this data directory out temporarily as it causes setup.py to throw errors
rm -rf %{_builddir}/puppet
mv packstack/puppet %{_builddir}/puppet


# build ------------------------------------------------------------------------

%build
%{__python} setup.py build

%if 0%{?with_doc}
cd docs
%if 0%{?rhel} == 6
make man SPHINXBUILD=sphinx-1.0-build
%else
make man
%endif
%endif


# install ----------------------------------------------------------------------

%install
%{__python} setup.py install --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

# Install Puppet module
mkdir -p %{buildroot}/%{_datadir}/openstack-puppet/modules
cp -r %{_builddir}/puppet/modules/packstack  %{buildroot}/%{_datadir}/openstack-puppet/modules/

# Move packstack documentation
mkdir -p %{buildroot}/%{_datadir}/packstack
install -p -D -m 644 docs/packstack.rst %{buildroot}/%{_datadir}/packstack

# Move Puppet manifest templates back to original place
mkdir -p %{buildroot}/%{python_sitelib}/packstack/puppet
mv %{_builddir}/puppet/templates %{buildroot}/%{python_sitelib}/packstack/puppet/

%if 0%{?with_doc}
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 docs/_build/man/*.1 %{buildroot}%{_mandir}/man1/
%endif

# Remove docs directory
rm -fr %{buildroot}%{python_sitelib}/docs

# files ------------------------------------------------------------------------

%files
%doc LICENSE
%{_bindir}/packstack
%{_datadir}/packstack
%{python_sitelib}/packstack
%{python_sitelib}/packstack-*.egg-info

%files puppet
%defattr(644,root,root,755)
%{_datadir}/openstack-puppet/modules/packstack

%if 0%{?with_doc}
%files doc
%{_mandir}/man1/packstack.1.gz
%endif


# changelog --------------------------------------------------------------------

%changelog
* Fri Apr 15 2016 Alan Pevec <apevec AT redhat.com> 8.0.0-0.8.0rc2
- Fix gate: Tempest setup and repositories

* Fri Apr 08 2016 Alan Pevec <apevec AT redhat.com> 8.0.0-0.7.0rc2
- Update to 8.0.0.0rc2
- Ensure aodh and horizon templates do not overwrite ports.conf
- Workaround for /dev/kvm permissions issues
- Packstack should not specify release when installint rdo repo

* Mon Apr 04 2016 Alan Pevec <apevec AT redhat.com> 8.0.0-0.4.0rc1
- Trove: use default api-paste.ini location

* Fri Apr 01 2016 Haikel Guemar <hguemar@fedoraproject.org> 8.0.0-0.3.0rc1
- Support new mariadb-server-galera package

* Thu Mar 24 2016 RDO <rdo-list@redhat.com> 8.0.0-0.1.0rc1
- RC1 Rebuild for Mitaka rc1
