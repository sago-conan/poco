import os, shutil
from conans import ConanFile, CMake


class PocoConan(ConanFile):
    name = "Poco"
    version = "1.9.0"
    license = "Boost Software License 1.0"
    url = "https://github.com/suwei-air/conan-poco"
    homepage = "https://pocoproject.org/"
    description = (
        "The POCO C++ Libraries are powerful cross-platform C++ libraries "
        "for building network- and internet-based applications "
        "that run on desktop, server, mobile, IoT, and embedded systems.")
    settings = "os", "compiler", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_encodings": [True, False],
        "enable_encodings_compiler": [True, False],
        "enable_xml": [True, False],
        "enable_json": [True, False],
        "enable_mongodb": [True, False],
        "enable_redis": [True, False],
        "enable_pdf": [True, False],
        "enable_util": [True, False],
        "enable_net": [True, False],
        "enable_netssl": [True, False],
        "enable_netssl_win": [True, False],
        "enable_crypto": [True, False],
        "enable_data": [True, False],
        "enable_data_sqlite": [True, False],
        "enable_data_mysql": [True, False],
        "enable_data_odbc": [True, False],
        "enable_sevenzip": [True, False],
        "enable_zip": [True, False],
        "enable_apacheconnector": [True, False],
        "enable_cppparser": [True, False],
        "enable_pocodoc": [True, False],
        "enable_pagecompiler": [True, False],
        "enable_pagecompiler_file2page": [True, False],
        "force_openssl": [True, False],
        "enable_tests": [True, False],
        "poco_unbundled": [True, False]
    }
    default_options = ("shared=False", "fPIC=True", "enable_encodings=True",
                       "enable_encodings_compiler=False", "enable_xml=True",
                       "enable_json=True", "enable_mongodb=False",
                       "enable_redis=False", "enable_pdf=False",
                       "enable_util=True", "enable_net=True",
                       "enable_netssl=False", "enable_netssl_win=False",
                       "enable_crypto=False", "enable_data=True",
                       "enable_data_sqlite=True", "enable_data_mysql=False",
                       "enable_data_odbc=False", "enable_sevenzip=False",
                       "enable_zip=True", "enable_apacheconnector=False",
                       "enable_cppparser=False", "enable_pocodoc=False",
                       "enable_pagecompiler=False",
                       "enable_pagecompiler_file2page=False",
                       "force_openssl=True", "enable_tests=False",
                       "poco_unbundled=False")
    generators = "cmake"
    exports_sources = "poco/*"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        cmake = CMake(self)
        for option_name in self.options.values.fields:
            activated = getattr(self.options, option_name)
            if option_name == "shared":
                cmake.definitions["POCO_STATIC"] = "OFF" if activated else "ON"
            elif not option_name == "fPIC":
                cmake.definitions[option_name.
                                  upper()] = "ON" if activated else "OFF"
        self.output.info(cmake.definitions)
        os.mkdir(".build")
        # Build debug & release
        if cmake.is_multi_configuration:
            cmake.configure(source_folder="poco", build_folder=".build")
            for config in ("Debug", "Release"):
                self.output.info("Building {}".format(config))
                cmake.build_type = config
                cmake.build()
        else:
            for config in ("Debug", "Release"):
                self.output.info("Building {}".format(config))
                cmake.build_type = config
                cmake.configure(source_folder="poco", build_folder=".build")
                cmake.build()
                shutil.rmtree("CMakeFiles")
                os.remove("CMakeCache.txt")

    def package(self):
        # Copy the license files
        self.copy("poco/LICENSE", dst=".", keep_path=False)
        # Typically includes we want to keep_path=True (default)
        packages = [
            "CppUnit", "Crypto", "Data", "Data/MySQL", "Data/ODBC",
            "Data/SQLite", "Foundation", "JSON", "MongoDB", "Net", "Redis",
            "Util", "XML", "Zip"
        ]
        if self.settings.os == "Windows" and self.options.enable_netssl_win:
            packages.append("NetSSL_Win")
        else:
            packages.append("NetSSL_OpenSSL")
        for header in packages:
            self.copy(
                pattern="*.h",
                dst="include",
                src="poco/{}/include".format(header))
        # But for libs and dlls, we want to avoid intermediate folders
        self.copy(
            pattern="*.lib", dst="lib", src=".build/lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=".build/lib", keep_path=False)
        self.copy(
            pattern="*.dll", dst="bin", src=".build/bin", keep_path=False)
        # in linux shared libs are in lib, not bin
        self.copy(
            pattern="*.so*",
            dst="lib",
            src=".build/lib",
            keep_path=False,
            symlinks=True)
        self.copy(
            pattern="*.dylib*", dst="lib", src=".build/lib", keep_path=False)

    def _append_lib(self, lib):
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            suffix = ["mdd", "md"]
        else:
            suffix = ["d", ""]
        self.cpp_info.debug.libs.append("{}{}".format(lib, suffix[0]))
        self.cpp_info.release.libs.append("{}{}".format(lib, suffix[1]))

    def package_info(self):
        libs = [("enable_mongodb", "PocoMongoDB"), ("enable_pdf", "PocoPDF"),
                ("enable_net", "PocoNet"), ("enable_netssl", "PocoNetSSL"),
                ("enable_netssl_win", "PocoNetSSLWin"),
                ("enable_crypto", "PocoCrypto"), ("enable_data", "PocoData"),
                ("enable_data_sqlite", "PocoDataSQLite"),
                ("enable_data_mysql", "PocoDataMySQL"),
                ("enable_data_odbc", "PocoDataODBC"),
                ("enable_sevenzip", "PocoSevenZip"), ("enable_zip", "PocoZip"),
                ("enable_apacheconnector", "PocoApacheConnector"),
                ("enable_util", "PocoUtil"), ("enable_xml", "PocoXML"),
                ("enable_json", "PocoJSON"), ("enable_redis", "PocoRedis")]
        for flag, lib in libs:
            if getattr(self.options, flag):
                if self.settings.os != "Windows" and flag == "enable_netssl_win":
                    continue
                self._append_lib(lib)
        self._append_lib("PocoFoundation")
        # in linux we need to link also with these libs
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "dl", "rt"])
        if not self.options.shared:
            self.cpp_info.defines.extend(
                ["POCO_STATIC=ON", "POCO_NO_AUTOMATIC_LIBS"])
            if self.settings.compiler == "Visual Studio":
                self.cpp_info.libs.extend(["ws2_32", "Iphlpapi", "Crypt32"])
