# @file edk2_coverage
# Handles coverage data for a given project.
##
# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
##
"""Invocable to process the coverage files generated by the host based unit tests.

Discovers and merges coverage files generating a report of the specified type and filtering
based on the settings files specifications.

Contains a CoverageSettingsManager that must be subclassed in a build settings
file. This provides the platform specific information for Edk2Coverage to handle
filtering the coverage data.
"""
import logging
from edk2toolext.invocables.edk2_multipkg_aware_invocable import Edk2MultiPkgAwareInvocable
from edk2toolext.invocables.edk2_multipkg_aware_invocable import MultiPkgAwareSettingsInterface
from edk2toollib.utility_functions import RunCmd


class CoverageSettingsManager(MultiPkgAwareSettingsInterface):
    """Platform specific settings for Edk2Coverage.

    Provide information necessary for `stuart_coverage.exe` or
    `edk2_coverage.py` to successfully execute.

    !!! example: "Example of Overriding CoverageSettingsManager"
        ```python
        from edk2toolext.invocables.edk2_coverage import CoverageSettingsManager
        class CiManager(CoverageSettingsManager):
            def GetCoverageExclusionList(self):
                return []

            def GetCoverageInclusionList(self):
                return []
        ```
    """

    def GetCoverageExclusionList(self):
        """Provide a list of file patterns to exclude from code coverage data.

        Returns:
            (list): list of file patterns to exclude from the code coverage report.
        """
        return []

    def GetCoverageInclusionList(self):
        """Provide a list of file patterns to include from code coverage data.

        Returns:
            (list): list of file patterns to include in the code coverage report.
        """
        return []


class Edk2Coverage(Edk2MultiPkgAwareInvocable):
    """Invocable to process the coverage files generated by the host based unit tests.

    Discover and merge coverage files generating a report of the specified type and filtering
    based on the settings files specifications.
    """

    def AddCommandLineOptions(self, parserObj):
        """Adds command line options to the argparser."""
        parserObj.add_argument('--coverage-files', dest="coverage_files", type=str, default="Build/**/coverage.xml",
                               help="Provide the paths to the coverage files")
        parserObj.add_argument('--report-type', dest="report_type", type=str, default="Cobertura",
                               help="Provide the type of report desired such as Cobertura or Html")
        parserObj.add_argument('--output-dir', dest="output_dir", type=str, default="Build/Coverage",
                               help="Provide directory where resulting files are placed")

        super().AddCommandLineOptions(parserObj)

    def RetrieveCommandLineOptions(self, args):
        """Retrieve command line options from the argparser."""
        self.coverage_files = args.coverage_files
        self.report_type = args.report_type
        self.output_dir = args.output_dir
        super().RetrieveCommandLineOptions(args)

    def GetVerifyCheckRequired(self):
        """Will not call self_describing_environment.VerifyEnvironment because it might not be set up yet."""
        return False

    def GetSettingsClass(self):
        """Returns the CoverageSettingsManager class.

        !!! warning
            CoverageSettingsManager must be subclassed in your platform settings file.
        """
        return CoverageSettingsManager

    def GetLoggingFileName(self, loggerType):
        """Returns the filename (COVERAGE) of where the logs for the Edk2CiBuild invocable are stored in."""
        return "COVERAGE"

    def Go(self):
        """Executes the core functionality of the Edk2CiBuild invocable."""
        # First, build up the inclusions and exclusion lists.
        includes = []
        excludes = ["*AutoGen.c", "*UnitTest*"]

        includes += self.PlatformSettings.GetCoverageInclusionList()
        excludes += self.PlatformSettings.GetCoverageExclusionList()

        if self.coverage_files is None:
            logging.error("Path to coverage file is required!\n")
            return -1

        file_filters = ""
        for file_path in excludes:
            if file_filters != "":
                file_filters += ";"
            file_filters += "-" + file_path
        for file_path in includes:
            if file_filters != "":
                file_filters += ";"
            file_filters += "+" + file_path

        args = " -reports:" + self.coverage_files
        args += " -targetdir:" + self.output_dir
        args += " -reporttypes:" + self.report_type
        args += " -filefilters:" + file_filters

        rc = RunCmd("reportgenerator", args)
        if rc == 0:
            logging.debug("reportgenerator command returned successfully!")
        else:
            logging.critical("reportgenerator returned error return value: %s" % str(rc))
            return rc

        return 0


def main():
    """Entry point invoke Edk2Coverage."""
    Edk2Coverage().Invoke()