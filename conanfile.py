from conan import ConanFile
import os


class LogicalGeometryConan(ConanFile):
    name = "logical-geometry"
    version = "1.1.0"
    license = "BSD-2-Clause"
    url = "https://gitlab.esss.lu.se/ecdc/ess-dmsc/logical-geometry"
    description = "Classes for mapping pixelid <-> (x,y,z,p)"
    exports_sources = "source/ESSGeometry.h"
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    def package(self):
        self.copy("ESSGeometry.h", dst=os.path.join("include", "logical_geometry"), src="source")

    def package_id(self):
        self.info.header_only()
