pipeline {
   agent {
       node {
           label 'linuxVM'
       }
   }

   stages {
      stage('Checkout SCM') {
         steps {
            dir('/home/joel/Projects/python/test/') {
               checkout([$class: 'GitSCM', branches: [[name: '*/master']],
                         doGenerateSubmoduleConfigurations: false,
                         //extensions: [[$class: 'CleanBeforeCheckout']],
                         extensions:[],
                         submoduleCfg: [],
                         userRemoteConfigs: [[credentialsId: '2928710d-6644-4296-bb91-78716f269a3d',
                                              url: 'https://github.com/BoxenOfDonuts/test-jenkins-2.git']]])
         }
            }
      }
      stage('Deploy Prod') {
         when { expression { return env.BRANCH_NAME == 'master'}  }
         environment {
             CONFIG_FILE=credentials('price-checker-config')
          }
          steps {
              echo 'Hello World'
              dir('/home/joel/Projects/python/test/') {
                 sh """
                 virtualenv venv
                 . venv/bin/activate
                 pip install -r requirements.txt
                 """
              }
              sh "cp ${CONFIG_FILE} /home/joel/Projects/python/test/"
              sh "cat /home/joel/Projects/python/test/config.ini"
         }
      }
      stage('Restart Service') {
         steps {
            build job: 'service restarter',
               parameters: [string(name: 'SERVICE_NAME', value: 'monitorpricecheck.service')]
         }
      }
   }
}
