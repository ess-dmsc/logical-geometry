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
                        make generate_coverage
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


////////////////////////////////////////

// def Object container_name(image_key) {
//     return "${base_container_name}-${image_key}"
// }
//
// def docker_checkout(image_key) {
//     def custom_sh = images[image_key]['sh']
//     stage("${image_key}: Checkout") {
//         sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
//             git clone \
//                 --branch ${env.BRANCH_NAME} \
//                 https://github.com/ess-dmsc/${project}.git
//         \""""
//     }
// }
//
// def docker_dependencies(image_key) {
//     def conan_remote = "ess-dmsc-local"
//     def custom_sh = images[image_key]['sh']
//     sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
//         cd ${project}
//         mkdir build
//         cd build
//         conan --version
//         conan remote add \
//             --insert 0 \
//             ${conan_remote} ${local_conan_server}
//         conan install .. --build=missing
//     \""""
// }
//
// def docker_cmake(image_key) {
//     cmake_exec = images[image_key]['cmake']
//     def custom_sh = images[image_key]['sh']
//     sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
//         cd ${project}/build
//         ${cmake_exec} --version
//         ${cmake_exec} -DCMAKE_BUILD_TYPE=Release ..
//     \""""
// }
//
// def docker_build(image_key) {
//     def custom_sh = images[image_key]['sh']
//     sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
//         cd ${project}/build
//         make --version
//         make unit_tests
//     \""""
// }
//
// def docker_tests(image_key) {
//     def custom_sh = images[image_key]['sh']
//     dir("${project}/tests") {
//         try {
//             sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
//                 cd ${project}/build
//                 make run_tests
//             \""""
//         } catch(e) {
//             sh "docker cp ${container_name(image_key)}:/home/jenkins/build/tests/unit_tests_run.xml unit_tests_run.xml"
//             junit 'unit_tests_run.xml'
//             failure_function(e, 'Run tests (${container_name(image_key)}) failed')
//         }
//     }
// }
//
// def docker_tests_coverage(image_key) {
//     def custom_sh = images[image_key]['sh']
//     abs_dir = pwd()
//
//     try {
//         sh "ls"
//         sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
//             cd ${project}/build
//             make generate_coverage
//         \""""
//         sh "docker cp ${container_name(image_key)}:/home/jenkins/${project} ./"
//         dir("${project}/build") {
//             sh "../jenkins/redirect_coverage.sh ./coverage/coverage.xml ${abs_dir}/${project}"
//             step([
//                 $class: 'CoberturaPublisher',
//                 autoUpdateHealth: true,
//                 autoUpdateStability: true,
//                 coberturaReportFile: 'coverage/coverage.xml',
//                 failUnhealthy: false,
//                 failUnstable: false,
//                 maxNumberOfBuilds: 0,
//                 onlyStable: false,
//                 sourceEncoding: 'ASCII',
//                 zoomCoverageChart: false
//             ])
//         }
//     } catch(e) {
//         failure_function(e, 'Run tests and coverage (${container_name(image_key)}) failed')
//     } finally {
//         sh "docker cp ${container_name(image_key)}:/home/jenkins/${project}/build/tests/unit_tests_run.xml unit_tests_run.xml"
//         junit 'unit_tests_run.xml'
//     }
// }
//
// def Object get_container(image_key) {
//     def image = docker.image(images[image_key]['name'])
//     def container = image.run("\
//         --name ${container_name(image_key)} \
//         --tty \
//         --network=host \
//         --env http_proxy=${env.http_proxy} \
//         --env https_proxy=${env.https_proxy} \
//         --env local_conan_server=${env.local_conan_server} \
//         ")
//     return container
// }
//
// def get_pipeline(image_key)
// {
//     return {
//         stage("${image_key}") {
//             node('docker') {
//                 try {
//                     def container = get_container(image_key)
//                     def custom_sh = images[image_key]['sh']
//
//                     sh "rm -rf ${project}"
//
//                     try {
//                         docker_checkout(image_key)
//                     } catch (e) {
//                         failure_function(e, "Checkout for ${image_key} failed")
//                     }
//
//                     try {
//                         docker_dependencies(image_key)
//                     } catch (e) {
//                         failure_function(e, "Get dependencies for ${image_key} failed")
//                     }
//
//                     try {
//                         docker_cmake(image_key)
//                     } catch (e) {
//                         failure_function(e, "CMake for ${image_key} failed")
//                     }
//
//                     try {
//                         docker_build(image_key)
//                     } catch (e) {
//                         failure_function(e, "Build for ${image_key} failed")
//                     }
//
//                     if (image_key == coverage_node) {
//                         docker_tests_coverage(image_key)
//                     } else {
//                         docker_tests(image_key)
//                     }
//                 } catch(e) {
//                     failure_function(e, "Unknown build failure for ${image_key}")
//                 } finally {
//                     sh "docker stop ${container_name(image_key)}"
//                     sh "docker rm -f ${container_name(image_key)}"
//                 }
//             }
//         }
//     }
// }

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

    //builders['macOS'] = get_macos_pipeline()

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



// node {
//     // Delete workspace when build is done
//     cleanWs()
//
//     stage('Checkout') {
//         scm_vars = checkout scm
//     }
//
//     def builders = [:]
//
//     for (x in images.keySet()) {
//         def image_key = x
//         builders[image_key] = get_pipeline(image_key)
//     }
//
//     parallel builders
// }
