%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%global pypi_name trove-dashboard
%global mod_name trove_dashboard

%bcond_without tests

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order bashate sphinx openstackdocstheme

Name:         openstack-trove-ui
Version:      XXX
Release:      XXX
Summary:      Trove Management Dashboard

License:      Apache-2.0
URL:          https://github.com/openstack/%{pypi_name}
Source0:      https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif
BuildArch:    noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif

BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
BuildRequires: gettext
BuildRequires: openstack-macros
# Required to compile translation files
BuildRequires: python3-django

Requires: openstack-dashboard
%description
OpenStack Dashboard plugin for Trove project

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{pypi_name}-%{upstream_version} -S git


# clean up
find -size 0 -not -name '__init__.py' -delete

sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

%generate_buildrequires
%if 0%{with tests}
  %pyproject_buildrequires -t -e %{default_toxenv}
%else
  %pyproject_buildrequires
%endif

%build
%pyproject_wheel

%install
%pyproject_install

# Generate i18n files
pushd %{buildroot}%{python3_sitelib}/%{mod_name}
django-admin compilemessages
popd

# Move config to horizon
mkdir -p  %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p  %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled

pushd .
cd %{buildroot}%{python3_sitelib}/%{mod_name}/enabled
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
mkdir -p  %{buildroot}%{python3_sitelib}/%{mod_name}/static
cp -rp %{mod_name}/static/* %{buildroot}%{python3_sitelib}/%{mod_name}/static/

# Remove .po and .pot (they are not required)
rm -f %{buildroot}%{python3_sitelib}/%{mod_name}/locale/*/LC_*/django*.po
rm -f %{buildroot}%{python3_sitelib}/%{mod_name}/locale/*pot

# Find language files
%find_lang django --all-name

%check
%if 0%{with tests}
%tox -e ${default_toxenv}
%endif

%files -f django.lang
%doc README.rst
%license LICENSE
%{python3_sitelib}/%{mod_name}
%{python3_sitelib}/*.dist-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1710_database_panel_group.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1720_project_databases_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1730_project_database_backups_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1731_project_database_backups_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1732_project_backup_strategies_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1740_project_database_clusters_panel.py*
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_1760_project_database_configurations_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1710_database_panel_group.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1720_project_databases_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1730_project_database_backups_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1731_project_database_backups_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1732_project_backup_strategies_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1740_project_database_clusters_panel.py*
%{_sysconfdir}/openstack-dashboard/enabled/_1760_project_database_configurations_panel.py*

%changelog
