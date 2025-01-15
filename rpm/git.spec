# Pass --without docs to rpmbuild if you don't want the documentation
%bcond_with                 docs
# Pass --without tests to rpmbuild if you don't want to run the tests
%bcond_with                 tests
%bcond_without              python3
%bcond_with                 cvs
%bcond_with                 p4
%global gitexecdir          %{_libexecdir}/git-core
%global use_new_rpm_filters 0
%global _pkgdocdir %{_docdir}/%{name}-%{version}
%global use_new_rpm_filters 1

Name:           git
Version:        2.48.1
Release:        1
Summary:        Fast Version Control System
License:        GPLv2
URL:            https://github.com/sailfishos/git
Source0:        %{name}-%{version}.tar.bz2

BuildRequires:  desktop-file-utils
BuildRequires:  expat-devel
BuildRequires:  findutils
BuildRequires:  gawk
BuildRequires:  gcc
BuildRequires:  gettext
BuildRequires:  gnupg2
BuildRequires:  libcurl-devel
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  perl
BuildRequires:  sed
BuildRequires:  tcl
BuildRequires:  zlib-devel >= 1.2

Requires:       git-core = %{version}-%{release}
Requires:       perl-Git = %{version}-%{release}

# Obsolete git-cvs if it's disabled
%if %{without cvs}
Obsoletes:      git-cvs < %{?epoch:%{epoch}:}%{version}-%{release}
%endif
# endif without cvs

# Obsolete git-p4 if it's disabled
%if %{without p4}
Obsoletes:      git-p4 < %{?epoch:%{epoch}:}%{version}-%{release}
%endif
# endif without p4

%description
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git rpm installs common set of tools which are usually using with
small amount of dependencies. To install all git packages, including
tools for integrating with other SCMs, install the git-all meta-package.

%package all
Summary:        Meta-package to pull in all git tools
BuildArch:      noarch
Requires:       git = %{version}-%{release}
Requires:       git-email = %{version}-%{release}
Requires:       git-gui = %{version}-%{release}
Requires:       git-subtree = %{version}-%{release}
Requires:       gitk = %{version}-%{release}
Requires:       perl-Git = %{version}-%{release}

%description all
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

This is a dummy package which brings in all subpackages.

%package core
Summary:        Core package of git with minimal functionality
Requires:       less
Requires:       openssh-clients
Requires:       zlib >= 1.2

%description core
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git-core rpm installs really the core tools with minimal
dependencies. Install git package for common set of tools.
To install all git packages, including tools for integrating with
other SCMs, install the git-all meta-package.

%package core-doc
Summary:        Documentation files for git-core
BuildArch:      noarch
Requires:       git-core = %{version}-%{release}

%description core-doc
Documentation files for git-core package including man pages.

%package email
Summary:        Git tools for sending patches via email
BuildArch:      noarch
Requires:       git = %{version}-%{release}
Requires:       perl(Authen::SASL)
Requires:       perl(Net::SMTP::SSL)

%description email
%{summary}.

%package -n gitk
Summary:        Git repository browser
BuildArch:      noarch
Requires:       git = %{version}-%{release}
Requires:       git-gui = %{version}-%{release}
Requires:       tk >= 8.4

%description -n gitk
%{summary}.

%package gui
Summary:        Graphical interface to Git
BuildArch:      noarch
Requires:       gitk = %{version}-%{release}
Requires:       tk >= 8.4

%description gui
%{summary}.

%package -n perl-Git
Summary:        Perl interface to Git
BuildArch:      noarch
Requires:       git = %{version}-%{release}
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description -n perl-Git
%{summary}.

%package -n perl-Git-SVN
Summary:        Perl interface to Git::SVN
BuildArch:      noarch
Requires:       git = %{version}-%{release}
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description -n perl-Git-SVN
%{summary}.

%package subtree
Summary:        Git tools to merge and split repositories
Requires:       git-core = %{version}-%{release}

%description subtree
Git subtrees allow subprojects to be included within a subdirectory
of the main project, optionally including the subproject's entire
history.

%prep
%autosetup -p1 -n %{name}-%{version}/%{name}

# Remove git-archimport from command list
sed -i '/^git-archimport/d' command-list.txt

# Use these same options for every invocation of 'make'.
# Otherwise it will rebuild in %%install due to flags changes.
# Pipe to tee to aid confirmation/verification of settings.
cat << \EOF | tee config.mak
V = 1
NEEDS_CRYPTO_WITH_SSL = 1
ETC_GITCONFIG = %{_sysconfdir}/gitconfig
INSTALL_SYMLINKS = 1
GNU_ROFF = 1
NO_PERL_CPAN_FALLBACKS = 1
NO_PYTHON = 1
NO_GITWEB = 1
htmldir = %{?_pkgdocdir}%{!?_pkgdocdir:%{_docdir}/%{name}-%{version}}
prefix = %{_prefix}
perllibdir = %{perl_vendorlib}

# Test options
DEFAULT_TEST_TARGET = prove
GIT_PROVE_OPTS = --verbose --normalize %{?_smp_mflags} --formatter=TAP::Formatter::File
GIT_TEST_OPTS = -x --verbose-log
EOF

# Filter bogus perl requires
# packed-refs comes from a comment in contrib/hooks/update-paranoid
%if %{use_new_rpm_filters}
%{?perl_default_filter}
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}perl\\(packed-refs\\)
%if ! %{defined perl_bootstrap}
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}perl\\(Term::ReadKey\\)
%endif
# endif ! defined perl_bootstrap
%else
cat << \EOF > %{name}-req
#!/bin/sh
%{__perl_requires} $* |\
sed -e '/perl(packed-refs)/d'
EOF

%global __perl_requires %{_builddir}/%{name}-%{version}/%{name}-req
chmod +x %{__perl_requires}
%endif
# endif use_new_rpm_filters

%build
# Improve build reproducibility
export TZ=UTC
export SOURCE_DATE_EPOCH=$(date -r version +%%s 2>/dev/null)

%make_build all %{?with_docs:docs}

%make_build -C contrib/contacts/ all

%make_build -C contrib/credential/netrc/

%make_build -C contrib/diff-highlight/

%make_build -C contrib/subtree/ all

# Remove contrib/fast-import/import-zips.py, contrib/hg-to-git, and
# contrib/svn-fe which all require python2.
rm -rf contrib/fast-import/import-zips.py contrib/hg-to-git contrib/svn-fe

%install
%make_install %{?with_docs:install-doc}

# Run install in contrib/contacts directory, since othervice install fails.
# Install gives a error "rm: cannot remove `contrib/contacts': Is a directory"
# For some reason it seems to run clean if executed in git directory.
#make_install -C contrib/contacts
pushd contrib/contacts
%make_install 
popd

# Run install in contrib/subtree directory, since othervice install fails.
# Install gives a error "rm: cannot remove `contrib/contacts': Is a directory"
# For some reason it seems to run clean if executed in git directory.
#make_install -C contrib/subtree
pushd contrib/subtree
%make_install 
popd

mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d

# install contrib/diff-highlight and clean up to avoid cruft in git-core-doc
install -Dpm 0755 contrib/diff-highlight/diff-highlight \
    %{buildroot}%{_datadir}/git-core/contrib/diff-highlight

rm -rf contrib/diff-highlight/{Makefile,diff-highlight,*.perl,t}
# Clean up contrib/subtree to avoid cruft in the git-core-doc docdir
rm -rf contrib/subtree/{INSTALL,Makefile,git-subtree*,t}

# git-archimport is not supported
find %{buildroot} Documentation -type f -name 'git-archimport*' -exec rm -f {} ';'

%if %{without cvs}
# Remove git-cvs* and gitcvs*
find %{buildroot} Documentation \( -type f -o -type l \) \
\( -name 'git-cvs*' -o -name 'gitcvs*' \) -exec rm -f {} ';'
%endif
# endif without cvs

%if %{without p4}
# Remove git-p4* and mergetools/p4merge
find %{buildroot} Documentation -type f -name 'git-p4*' -exec rm -f {} ';'
rm -f %{buildroot}%{gitexecdir}/mergetools/p4merge
%endif
# endif without p4

# Remove unneeded git-remote-testsvn so git-svn can be noarch
rm -f %{buildroot}%{gitexecdir}/git-remote-testsvn

exclude_re="archimport|email|git-(citool|cvs|daemon|gui|instaweb|p4|subtree|svn)|gitk|gitweb|p4merge"
(find %{buildroot}{%{_bindir},%{_libexecdir}} -type f -o -type l | grep -vE "$exclude_re" | sed -e s@^%{buildroot}@@) > bin-man-doc-files
(find %{buildroot}{%{_bindir},%{_libexecdir}} -mindepth 1 -type d | grep -vE "$exclude_re" | sed -e 's@^%{buildroot}@%%dir @') >> bin-man-doc-files

(find %{buildroot}%{perl_vendorlib} -type f | sed -e s@^%{buildroot}@@) > perl-git-files
(find %{buildroot}%{perl_vendorlib} -mindepth 1 -type d | sed -e 's@^%{buildroot}@%dir @') >> perl-git-files

# Split out Git::SVN files
grep Git/SVN perl-git-files > perl-git-svn-files
sed -i "/Git\/SVN/ d" perl-git-files

%if %{with docs}
(find %{buildroot}%{_mandir} -type f | grep -vE "$exclude_re|Git" | sed -e s@^%{buildroot}@@ -e 's/$/*/' ) >> bin-man-doc-files
%else
rm -rf %{buildroot}%{_mandir}
%endif
# endif with docs

mkdir -p %{buildroot}%{_localstatedir}/lib/git

# Install tcsh completion
mkdir -p %{buildroot}%{_datadir}/git-core/contrib/completion
install -pm 644 contrib/completion/git-completion.tcsh \
    %{buildroot}%{_datadir}/git-core/contrib/completion/

# Move contrib/hooks out of %%docdir
mkdir -p %{buildroot}%{_datadir}/git-core/contrib
mv contrib/hooks %{buildroot}%{_datadir}/git-core/contrib
pushd contrib > /dev/null
ln -s ../../../git-core/contrib/hooks
popd > /dev/null

# Install git-prompt.sh
mkdir -p %{buildroot}%{_datadir}/git-core/contrib/completion
install -pm 644 contrib/completion/git-prompt.sh \
    %{buildroot}%{_datadir}/git-core/contrib/completion/

# symlink git-citool to git-gui if they are identical
pushd %{buildroot}%{gitexecdir} >/dev/null
if cmp -s git-gui git-citool 2>/dev/null; then
    ln -svf git-gui git-citool
fi
popd >/dev/null

# find translations
%find_lang %{name} %{name}.lang
cat %{name}.lang >> bin-man-doc-files

# quiet some rpmlint complaints
chmod -R g-w %{buildroot}
chmod a-x %{buildroot}%{gitexecdir}/git-mergetool--lib

# These files probably are not needed
find . -regex '.*/\.\(git\(attributes\|ignore\)\|perlcriticrc\)' -delete
chmod a-x Documentation/technical/api-index.sh
find contrib -type f -print0 | xargs -r0 chmod -x

# Split core files
not_core_re="git-(add--interactive|contacts|credential-(libsecret|netrc)|difftool|filter-branch|instaweb|request-pull|send-mail)|gitweb"
grep -vE "$not_core_re|%{_mandir}" bin-man-doc-files > bin-files-core
touch man-doc-files-core
%if %{with docs}
grep -vE "$not_core_re" bin-man-doc-files | grep "%{_mandir}" > man-doc-files-core
%endif
# endif with docs
grep -E "$not_core_re" bin-man-doc-files > bin-man-doc-git-files

##### DOC
# place doc files into %%{_pkgdocdir} and split them into expected packages
# contrib
not_core_doc_re="(git-(cvs|gui|citool|daemon|instaweb|subtree))|p4|svn|email|gitk|gitweb"

mkdir -p %{buildroot}%{_pkgdocdir}/
cp -pr CODE_OF_CONDUCT.md README.md Documentation/*.txt Documentation/RelNotes contrib %{buildroot}%{_pkgdocdir}/

# Remove contrib/ files/dirs which have nothing useful for documentation
rm -rf %{buildroot}%{_pkgdocdir}/contrib/{contacts,credential,svn-fe}/

# Remove unneeded gitweb and instaweb files
rm -f %{buildroot}%{gitexecdir}/git-instaweb
rm -f %{buildroot}%{_pkgdocdir}/git-instaweb.txt
rm -f %{buildroot}%{_pkgdocdir}/gitweb.conf.txt
rm -f %{buildroot}%{_pkgdocdir}/gitweb.txt

# Remove unneeded git-daemon files
rm -f %{buildroot}%{gitexecdir}/git-daemon
rm -f %{buildroot}%{_pkgdocdir}/git-daemon.txt

%if %{with docs}
cp -pr Documentation/*.html Documentation/docbook-xsl.css %{buildroot}%{_pkgdocdir}/
cp -pr Documentation/{howto,technical} %{buildroot}%{_pkgdocdir}/
find %{buildroot}%{_pkgdocdir}/{howto,technical} -type f \
    |grep -o "%{_pkgdocdir}.*$" >> man-doc-files-core
%endif
# endif with docs

{
    find %{buildroot}%{_pkgdocdir} -type f -maxdepth 1 \
        | grep -o "%{_pkgdocdir}.*$" \
        | grep -vE "$not_core_doc_re"
    find %{buildroot}%{_pkgdocdir}/{contrib,RelNotes} -type f \
        | grep -o "%{_pkgdocdir}.*$"
    find %{buildroot}%{_pkgdocdir} -type d | grep -o "%{_pkgdocdir}.*$" \
        | sed "s/^/\%dir /"
} >> man-doc-files-core
##### DOC

%check
%if %{without tests}
exit 0
%endif
# endif without tests

%files -f bin-man-doc-git-files
%{_datadir}/git-core/contrib/diff-highlight
%{_datadir}/git-core/contrib/hooks/update-paranoid
%{_datadir}/git-core/contrib/hooks/setgitperms.perl
%{_datadir}/git-core/templates/hooks/fsmonitor-watchman.sample
%{_datadir}/git-core/templates/hooks/pre-rebase.sample
%{_datadir}/git-core/templates/hooks/prepare-commit-msg.sample

%files all
# No files for you!

%files core -f bin-files-core
#NOTE: this is only use of the %%doc macro in this spec file and should not
#      be used elsewhere
%{!?_licensedir:%global license %doc}
%license COPYING
# exclude is best way here because of troubles with symlinks inside git-core/
%exclude %{_datadir}/git-core/contrib/diff-highlight
%exclude %{_datadir}/git-core/contrib/hooks/update-paranoid
%exclude %{_datadir}/git-core/contrib/hooks/setgitperms.perl
%exclude %{_datadir}/git-core/templates/hooks/fsmonitor-watchman.sample
%exclude %{_datadir}/git-core/templates/hooks/pre-rebase.sample
%exclude %{_datadir}/git-core/templates/hooks/prepare-commit-msg.sample
%{_datadir}/git-core/

%files core-doc -f man-doc-files-core
%{_pkgdocdir}/contrib/hooks

%files email
%{_pkgdocdir}/*email*.txt
%{gitexecdir}/*email*
%{?with_docs:%{_mandir}/man1/*email*.1*}
%{?with_docs:%{_pkgdocdir}/*email*.html}

%files -n gitk
%{_pkgdocdir}/*gitk*.txt
%{_bindir}/*gitk*
%{_datadir}/gitk
%{?with_docs:%{_mandir}/man1/*gitk*.1*}
%{?with_docs:%{_pkgdocdir}/*gitk*.html}

%files gui
%{gitexecdir}/git-gui*
%{gitexecdir}/git-citool
%{_datadir}/git-gui/
%{_pkgdocdir}/git-gui.txt
%{_pkgdocdir}/git-citool.txt
%{?with_docs:%{_mandir}/man1/git-gui.1*}
%{?with_docs:%{_pkgdocdir}/git-gui.html}
%{?with_docs:%{_mandir}/man1/git-citool.1*}
%{?with_docs:%{_pkgdocdir}/git-citool.html}

%files -n perl-Git -f perl-git-files
%{?with_docs:%{_mandir}/man3/Git.3pm*}

%files -n perl-Git-SVN -f perl-git-svn-files

%files subtree
%{gitexecdir}/git-subtree
%{gitexecdir}/git-svn
%{_pkgdocdir}/git-svn.txt

