project = "logical-geometry"

images = [
    'centos7': [
        'name': 'essdmscdm/centos7-build-node:3.0.0',
        'sh': '/usr/bin/scl enable devtoolset-6 -- /bin/bash -e',
        'cmake': 'cmake3 -DCOV=1'
    ],
    'ubuntu1804': [
        'name': 'essdmscdm/ubuntu18.04-build-node:1.1.0',
        'sh': 'bash -e',
        'cmake': 'cmake'
    ]
]

coverage_node = 'centos7'

base_container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

def failure_function(exception_obj, failureMessage) {
    def toEmails = [[$class: 'DevelopersRecipientProvider']]
    emailext body: '${DEFAULT_CONTENT}\n\"' + failureMessage +'\"\n\nCheck console output at $BUILD_URL to view the results.',
        recipientProviders: toEmails,
        subject: '${DEFAULT_SUBJECT}'
    slackSend color: 'danger',
        message: "@afonso.mukai ${project}-${env.BRANCH_NAME}: " + failureMessage

    throw exception_obj
}

def Object container_name(image_key) {
    return "${base_container_name}-${image_key}"
}

def docker_checkout(image_key) {
    def custom_sh = images[image_key]['sh']
    stage("${image_key}: Checkout") {
        sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
            git clone \
                --branch ${env.BRANCH_NAME} \
                https://github.com/ess-dmsc/${project}.git
        \""""
    }
}

def docker_dependencies(image_key) {
    def conan_remote = "ess-dmsc-local"
    def custom_sh = images[image_key]['sh']
    sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
        mkdir build
        cd build
        conan --version
        conan remote add \
            --insert 0 \
            ${conan_remote} ${local_conan_server}
        conan install ../${project} --build=missing
    \""""
}

def docker_cmake(image_key) {
    cmake_exec = images[image_key]['cmake']
    def custom_sh = images[image_key]['sh']
    sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
        cd build
        ${cmake_exec} --version
        ${cmake_exec} -DCMAKE_BUILD_TYPE=Release ../${project}
    \""""
}

def docker_build(image_key) {
    def custom_sh = images[image_key]['sh']
    sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
        cd build
        make --version
        make unit_tests
    \""""
}

def docker_tests(image_key) {
    def custom_sh = images[image_key]['sh']
    dir("${project}/tests") {
        try {
            sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
                cd build
                make run_tests
            \""""
        } catch(e) {
            sh "docker cp ${container_name(image_key)}:/home/jenkins/build/test/unit_tests_run.xml unit_tests_run.xml"
            junit 'unit_tests_run.xml'
            failure_function(e, 'Run tests (${container_name(image_key)}) failed')
        }
    }
}

def docker_tests_coverage(image_key) {
    def custom_sh = images[image_key]['sh']
    abs_dir = pwd()

    try {
        sh """docker exec ${container_name(image_key)} ${custom_sh} -c \"
            cd build
            make generate_coverage
        \""""
        sh "docker cp ${container_name(image_key)}:/home/jenkins/${project} ./"
        dir("${project}/build") {
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
                zoomCoverageChart: false
            ])
        }
    } catch(e) {
        failure_function(e, 'Run tests and coverage (${container_name(image_key)}) failed')
    } finally {
        sh "docker cp ${container_name(image_key)}:/home/jenkins/build/test/unit_tests_run.xml unit_tests_run.xml"
        junit 'unit_tests_run.xml'
    }
}

def Object get_container(image_key) {
    def image = docker.image(images[image_key]['name'])
    def container = image.run("\
        --name ${container_name(image_key)} \
        --tty \
        --network=host \
        --env http_proxy=${env.http_proxy} \
        --env https_proxy=${env.https_proxy} \
        --env local_conan_server=${env.local_conan_server} \
        ")
    return container
}

def get_pipeline(image_key)
{
    return {
        stage("${image_key}") {
            node('docker') {
                try {
                    def container = get_container(image_key)
                    def custom_sh = images[image_key]['sh']

                    sh "rm -rf ${project}"

                    try {
                        docker_checkout(image_key)
                    } catch (e) {
                        failure_function(e, "Checkout for ${image_key} failed")
                    }

                    try {
                        docker_dependencies(image_key)
                    } catch (e) {
                        failure_function(e, "Get dependencies for ${image_key} failed")
                    }

                    try {
                        docker_cmake(image_key)
                    } catch (e) {
                        failure_function(e, "CMake for ${image_key} failed")
                    }

                    try {
                        docker_build(image_key)
                    } catch (e) {
                        failure_function(e, "Build for ${image_key} failed")
                    }

                    if (image_key == coverage_node) {
                        docker_tests_coverage(image_key)
                    } else {
                        docker_tests(image_key)
                    }
                } catch(e) {
                    failure_function(e, "Unknown build failure for ${image_key}")
                } finally {
                    sh "docker stop ${container_name(image_key)}"
                    sh "docker rm -f ${container_name(image_key)}"
                }
            }
        }
    }
}

node {
    // Delete workspace when build is done
    cleanWs()

    stage('Checkout') {
        scm_vars = checkout scm
    }

    def builders = [:]

    for (x in images.keySet()) {
        def image_key = x
        builders[image_key] = get_pipeline(image_key)
    }

    parallel builders
}
