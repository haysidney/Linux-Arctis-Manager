# Copyright 2025 Sidney Hays
# Distributed under the terms of the GNU General Public License v3

EAPI=8

PYTHON_COMPAT=( python3_{11..13} )
DISTUTILS_USE_PEP517=hatchling

inherit distutils-r1 git-r3 systemd

DESCRIPTION="Replacement for SteelSeries GG software to manage Arctis devices on Linux"
HOMEPAGE="https://github.com/haysidney/Linux-Arctis-Manager"
EGIT_REPO_URI="https://github.com/haysidney/Linux-Arctis-Manager"
EGIT_BRANCH="feature/arctis-7-support"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64"
IUSE="gui"

RDEPEND="
	dev-python/dbus-next[${PYTHON_USEDEP}]
	dev-python/pulsectl[${PYTHON_USEDEP}]
	dev-python/pyudev[${PYTHON_USEDEP}]
	dev-python/pyusb[${PYTHON_USEDEP}]
	dev-python/ruamel-yaml[${PYTHON_USEDEP}]
	gui? ( dev-python/pyside[${PYTHON_USEDEP}] )
"
DEPEND="${RDEPEND}"

src_install() {
	distutils-r1_src_install
	systemd_douserunit scripts/arctis-manager.service
}
