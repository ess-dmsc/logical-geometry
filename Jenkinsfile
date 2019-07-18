@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.PipelineBuilder

project = "logical-geometry"
coverage_on = "centos7"
clangformat_os = "debian9"

// Set number of old builds to keep.
 properties([[
     $class: 'BuildDiscarderProperty',
     strategy: [
         $class: 'LogRotator',
         artifactDaysToKeepStr: '',
         artifactNumToKeepStr: '10',
         daysToKeepStr: '',
         numToKeepStr: ''
     ]
 ]]);

container_build_nodes = [
  'centos7': ContainerBuildNode.getDefaultContainerBuildNode('centos7'),
  'debian9': ContainerBuildNode.getDefaultContainerBuildNode('debian9'),
  'ubuntu1804': ContainerBuildNode.getDefaultContainerBuildNode('ubuntu1804')
]

def failure_function(exception_obj, failureMessage) {
    def toEmails = [[$class: 'DevelopersRecipientProvider']]
    emailext body: '${DEFAULT_CONTENT}\n\"' + failureMessage + '\"\n\nCheck console output at $BUILD_URL to view the results.',
            recipientProviders: toEmails,
            subject: '${DEFAULT_SUBJECT}'
    throw exception_obj
}

pipeline_builder = new PipelineBuilder(this, container_build_nodes)
pipeline_builder.activateEmailFailureNotifications()


builders = pipeline_builder.createBuilders { container ->

    pipeline_builder.stage("${container.key}: checkout") {
        dir(pipeline_builder.project) {
            scm_vars = checkout scm
        }
        // Copy source code to container
        container.copyTo(pipeline_builder.project, pipeline_builder.project)
    }  // stage


    if (container.key != clangformat_os) {
        pipeline_builder.stage("${container.key}: get dependencies") {
            container.sh """
                cd ${project}
                mkdir build
                cd build
                conan remote add --insert 0 ess-dmsc-local ${local_conan_server}
                conan install --build=outdated ..
            """
        }  // stage


        pipeline_builder.stage("${container.key}: configure") {
            def xtra_flags = ""
            if (container.key == coverage_on) {
                xtra_flags = "-DCOV=ON"
            }
            container.sh """
                cd ${project}/build
                cmake --version
                cmake -DCONAN=MANUAL ${xtra_flags} ..
            """
        }  // stage

        pipeline_builder.stage("${container.key}: build") {
            container.sh """
                cd ${project}/build
                make --version
                make unit_tests -j4
            """
        }  // stage
    }

    if (container.key == clangformat_os) {
        pipeline_builder.stage("${container.key}: cppcheck") {
        try {
                def test_output = "cppcheck.txt"
                container.sh """
                                cd ${project}
                                cppcheck --enable=all --inconclusive --template="{file},{line},{severity},{id},{message}" ./ 2> ${test_output}
                            """
                container.copyFrom("${project}", '.')
                sh "mv -f ./${project}/* ./"
            } catch (e) {
                failure_function(e, "Cppcheck step for (${container.key}) failed")
            }
        }  // stage
        step([$class: 'WarningsPublisher', parserConfigurations: [[parserName: 'Cppcheck Parser', pattern: "cppcheck.txt"]]])
    }

    if (container.key == coverage_on) {
        pipeline_builder.stage("${container.key}: test coverage") {
            abs_dir = pwd()

            try {
                container.sh """
                        cd ${project}/build
                        make coverage
                    """
                container.copyFrom("${project}", '.')
            } catch(e) {
                container.copyFrom("${project}/build/tests", '.')
                junit 'tests/*.xml'
                failure_function(e, 'Run tests (${container.key}) failed')
            }

            dir("${project}/build") {
                    junit 'tests/*.xml'
                    sh "../jenkins/redirect_coverage.sh ./coverage/coverage.xml ${abs_dir}/${project}"

                    step([
                        $class: 'CoberturaPublisher',
                        autoUpdateHealth: true,
                        autoUpdateStability: true,
                        coberturaReportFile: 'coverage/coverage.xml',
                        failUnhealthy: false,
                        failUnstable: false,
                        maxNumberOfBuilds: 0,
                        onlyStable: false,
                        sourceEncoding: 'ASCII',
                        zoomCoverageChart: true
                    ])
            }
        }  // stage
    } else if (container.key != clangformat_os) {
        pipeline_builder.stage("${container.key}: tests") {
            container.sh """
                cd ${project}/build
                make run_tests
            """
        }  // stage
    }
}

def get_macos_pipeline()
{
    return {
        stage("macOS") {
            node ("macos") {
                // Delete workspace when build is done
                cleanWs()

                abs_dir = pwd()

                dir("${project}") {
                    checkout scm
                }

                dir("${project}/build") {
                    sh "conan install --build=outdated .."
                    sh "cmake -DCONAN=MANUAL -DCMAKE_MACOSX_RPATH=ON .."
                    sh "make run_tests"
                }
            }
        }
    }
}


node('docker') {
    dir("${project}_code") {

        stage('Checkout') {
            try {
                scm_vars = checkout scm
            } catch (e) {
                failure_function(e, 'Checkout failed')
            }
        }

        stage("Static analysis") {
            try {
                sh "find . -name '*TestData.h' > exclude_cloc"
                sh "cloc --exclude-list-file=exclude_cloc --by-file --xml --out=cloc.xml ."
                sh "xsltproc jenkins/cloc2sloccount.xsl cloc.xml > sloccount.sc"
                sloccountPublish encoding: '', pattern: ''
            } catch (e) {
                failure_function(e, 'Static analysis failed')
            }
        }
    }

    builders['macOS'] = get_macos_pipeline()

    try {
        timeout(time: 2, unit: 'HOURS') {
            parallel builders
        }
    } catch (e) {
        failure_function(e, 'Job failed')
        throw e
    } finally {
        // Delete workspace when build is done
        cleanWs()
    }
}
