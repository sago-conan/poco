from cpt.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="Poco:shared", pure_c=False)
    builder.remove_build_if(
        lambda build: ("compiler.libcxx" in build.settings and build.settings["compiler.libcxx"] == "libstdc++") or ("compiler.runtime" in build.settings and build.settings["compiler.runtime"].startswith("MT"))
    )
    builder.run()
