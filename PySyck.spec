Summary: Python bindings for the Syck YAML parser and emitter
Name: PySyck
Version: 0.61.2
Release: 1
License: BSD
Group: Development/Libraries
URL: http://pyyaml.org/wiki/PySyck
Source: http://pyyaml.org/download/pysyck/%{name}-%{version}.tar.gz
BuildRequires: byacc, flex, bison
BuildRoot: %{_tmppath}/%{name}-root

%description
Syck is an extension for reading and writing YAML swiftly in popular
scripting languages. As Syck loads the YAML, it stores the data directly in
your language's symbol table.

PySyck is aimed to update the current Python bindings for Syck. The new bindings provide a wrapper for the Syck emitter and give access to YAML representation graphs. Hopefully it will not leak memory as well.

PySyck may be used for various tasks, in particular, as a replacement of the module pickle.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf ${RPM_BUILD_ROOT}
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
chmod +x $RPM_BUILD_ROOT%{python_sitelib}/syck/*.py

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-, root, root)
%doc PKG-INFO  README.html  README.txt
%{python_sitelib}/syck/
%{python_sitelib}/_syck.so

%changelog
* Sat Mar 25 2006 Jeff Johnson <jbj@jbj.org> 0.61.1-2
- upgrade to 0.61.2.

* Sat Mar 18 2006 Jeff Johnson <jbj@jbj.org> 0.61.1-1
- create.
