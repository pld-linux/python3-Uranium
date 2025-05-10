#
# Conditional build:
%bcond_with	tests	# test suite

%define		module		Uranium
Summary:	A Python framework for building desktop applications
Summary(pl.UTF-8):	Szkielet Pythona do tworzenia aplikacji graficznych
Name:		python3-%{module}
# keep in sync with CuraEngine, cura, libArcus, libSavitar
Version:	4.13.2
Release:	4
License:	AGPL v3+
Group:		Libraries/Python
#Source0Download: https://github.com/Ultimaker/Uranium/tags
Source0:	https://github.com/Ultimaker/Uranium/archive/%{version}/%{module}-%{version}.tar.gz
# Source0-md5:	be9516a605fe1f6160711a746864774f
Patch0:		remove-mypy-test.patch
Patch1:		plugins-path.patch
URL:		https://github.com/Ultimaker/Uranium
BuildRequires:	cmake >= 3.6
BuildRequires:	doxygen
BuildRequires:	gettext-tools
BuildRequires:	python3-Arcus = %{version}
BuildRequires:	python3-devel
BuildRequires:	python3-numpy
BuildRequires:	python3-PyQt5-devel
BuildRequires:	python3-pytest
BuildRequires:	python3-scipy
BuildRequires:	python3-shapely
Requires:	python3-Arcus = %{version}
Requires:	python3-PyQt5
Requires:	python3-numpy
Requires:	python3-scipy
Requires:	python3-shapely
Obsoletes:	python3-UM < 0.2
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Uranium is a Python framework for building 3D printing related
applications.

%description -l pl.UTF-8
Uranium to pythonowy szkielt do tworzenia aplikacji związanych z
drukiem 3D.

%package doc
Summary:	Documentation for Python Uranium library
Summary(pl.UTF-8):	Dokumentacja do biblioteki Pythona Uranium
Group:		Documentation

%description doc
Documentation for Uranium, a Python framework for building 3D printing
related applications.

%description doc -l pl.UTF-8
Dokumentacja do Uranium - szkieletu pythonowego do tworzenia aplikacji
związanych z drukiem 3D.

%prep
%setup -q -n %{module}-%{version}
%patch -P 0 -p1
%patch -P 1 -p1

for bad_lang in cs_CZ de_DE es_ES fi_FI fr_FR hu_HU it_IT ja_JP ko_KR nl_NL pl_PL pt_PT ru_RU tr_TR ; do
	lang="$(echo $bad_lang | sed 's/_.*//')"
	%{__mv} "resources/i18n/$bad_lang" "resources/i18n/$lang"
done

# Upstream installs to lib/python3/dist-packages
# We want to install to %%{py3_sitescriptdir}
sed -i 's|lib${LIB_SUFFIX}/python${PYTHON_VERSION_MAJOR}.*/.*-packages|%(echo %{py3_sitescriptdir} | sed -e s@%{_prefix}/@@)|g' CMakeLists.txt

# empty file. appending to the end to make sure we are not overriding
# a non empty file in the future
echo '# empty' >> UM/Settings/ContainerRegistryInterface.py

# The failing test is reported at https://github.com/Ultimaker/Uranium/issues/225
%{__rm} -r tests/MimeTypes

%build
mkdir build
cd build
%{cmake} ..
%{__make}
%{__make} doc

%{?with_tests:%{__make} test}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

# Move the cmake files
%{__mv} $RPM_BUILD_ROOT%{_datadir}/cmake* $RPM_BUILD_ROOT%{_datadir}/cmake

# Sanitize the location of locale files
%{__mv} $RPM_BUILD_ROOT%{_datadir}/{uranium/resources/i18n,locale}
ln -s ../../locale $RPM_BUILD_ROOT%{_datadir}/uranium/resources/i18n
%{__rm} $RPM_BUILD_ROOT%{_localedir}/uranium.pot
%{__rm} $RPM_BUILD_ROOT%{_localedir}/*/uranium.po

%find_lang uranium

%clean
rm -rf $RPM_BUILD_ROOT

%files -f uranium.lang
%defattr(644,root,root,755)
%doc README.md
%{py3_sitescriptdir}/UM
%{_datadir}/uranium
%{_datadir}/cmake

%files doc
%defattr(644,root,root,755)
%doc html/*
