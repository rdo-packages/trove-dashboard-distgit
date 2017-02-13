%global milestone .0rc1
%global pypi_name trove-dashboard
%global mod_name trove_dashboard

# tests are disabled by default
%bcond_with tests

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:         openstack-trove-ui
Version:      8.0.0
Release:      0.1%{?milestone}%{?dist}
Summary:      Trove Management Dashboard

License:      ASL 2.0
URL:          https://github.com/openstack/%{pypi_name}
Source0:      https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
#
# patches_base=8.0.0.0rc1
#

BuildArch:    noarch

BuildRequires: python2-devel
BuildRequires: python-pbr
BuildRequires: python-sphinx
BuildRequires: python-oslo-sphinx
# Required to compile translation files
BuildRequires: python-django
BuildRequires: gettext

Requires: python-babel
Requires: openstack-dashboard
Requires: python-iso8601
Requires: python-keystoneclient
Requires: python-swiftclient
Requires: python-troveclient

%description
OpenStack Dashboard plugin for Trove project

%prep
%setup -q -n %{pypi_name}-%{upstream_version}

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires
rm -rf %{pypi_name}.egg-info

# clean up
find -size 0 -not -name '__init__.py' -delete

%build
%{__python2} setup.py build
# Generate i18n files
pushd build/lib/%{mod_name}
django-admin compilemessages
popd

%install
%{__python2} setup.py install --skip-build --root %{buildroot}

# Move config to horizon
mkdir -p  %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled

pushd .
cd %{buildroot}%{python2_sitelib}/%{mod_name}/enabled
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
mkdir -p  %{buildroot}%{python2_sitelib}/%{mod_name}/static
cp -rp %{mod_name}/static/* %{buildroot}%{python2_sitelib}/%{mod_name}/static/

# Remove .po and .pot (they are not required)
rm -f %{buildroot}%{python2_sitelib}/%{mod_name}/locale/*/LC_*/django*.po
rm -f %{buildroot}%{python2_sitelib}/%{mod_name}/locale/*pot

# Find language files
%find_lang django --all-name

%check
%if 0%{with tests}
PYTHONPATH=/usr/share/openstack-dashboard/ ./run_tests.sh -N -P
%endif

%files -f django.lang
%doc README.rst
%license LICENSE
%{python2_sitelib}/%{mod_name}
%{python2_sitelib}/*.egg-info
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
* Mon Feb 13 2017 Alfredo Moralejo <amoralej@redhat.com> 8.0.0-0.1.0rc1
- Update to 8.0.0.0rc1


