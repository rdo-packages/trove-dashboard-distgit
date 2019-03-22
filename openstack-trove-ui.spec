%global milestone .0rc1
# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%global pypi_name trove-dashboard
%global mod_name trove_dashboard

# tests are disabled by default
%bcond_with tests

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:         openstack-trove-ui
Version:      12.0.0
Release:      0.1%{?milestone}%{?dist}
Summary:      Trove Management Dashboard

License:      ASL 2.0
URL:          https://github.com/openstack/%{pypi_name}
Source0:      https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
#
# patches_base=12.0.0.0rc1
#

BuildArch:    noarch

BuildRequires: python%{pyver}-devel
BuildRequires: python%{pyver}-pbr
BuildRequires: python%{pyver}-sphinx
BuildRequires: python%{pyver}-oslo-sphinx
# Required to compile translation files
BuildRequires: python%{pyver}-django
BuildRequires: gettext
BuildRequires: openstack-macros

Requires: openstack-dashboard
Requires: python%{pyver}-swiftclient >= 2.2.0
Requires: python%{pyver}-troveclient >= 1.2.0
Requires: python%{pyver}-oslo-log >= 3.30.0
Requires: python%{pyver}-pbr >= 1.6

%description
OpenStack Dashboard plugin for Trove project

%prep
%setup -q -n %{pypi_name}-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup
rm -rf %{pypi_name}.egg-info

# clean up
find -size 0 -not -name '__init__.py' -delete

%build
%{pyver_build}
# Generate i18n files
pushd build/lib/%{mod_name}
django-admin compilemessages
popd

%install
%{pyver_install}

# Move config to horizon
mkdir -p  %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled

pushd .
cd %{buildroot}%{pyver_sitelib}/%{mod_name}/enabled
for f in _17*.py*; do
    cp -p ${f} %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/
done
popd

for f in %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_17*.py*; do
    filename=`basename $f`
    ln -s %{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/${filename} \
        %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/${filename}
done

# Move static files to horizon. These require that you compile them again
# post install { python manage.py compress }
mkdir -p  %{buildroot}%{pyver_sitelib}/%{mod_name}/static
cp -rp %{mod_name}/static/* %{buildroot}%{pyver_sitelib}/%{mod_name}/static/

# Remove .po and .pot (they are not required)
rm -f %{buildroot}%{pyver_sitelib}/%{mod_name}/locale/*/LC_*/django*.po
rm -f %{buildroot}%{pyver_sitelib}/%{mod_name}/locale/*pot

# Find language files
%find_lang django --all-name

%check
%if 0%{with tests}
PYTHONPATH=/usr/share/openstack-dashboard/ ./run_tests.sh -N -P
%endif

%files -f django.lang
%doc README.rst
%license LICENSE
%{pyver_sitelib}/%{mod_name}
%{pyver_sitelib}/*.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1710_database_panel_group.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1720_project_databases_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1730_project_database_backups_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1731_project_database_backups_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1740_project_database_clusters_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1760_project_database_configurations_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1710_database_panel_group.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1720_project_databases_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1730_project_database_backups_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1731_project_database_backups_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1740_project_database_clusters_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1760_project_database_configurations_panel.py*

%changelog
* Fri Mar 22 2019 RDO <dev@lists.rdoproject.org> 12.0.0-0.1.0rc1
- Update to 12.0.0.0rc1


