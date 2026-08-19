pipeline {
    agent any 

    stages {
        stage("Checkout latest code"){
            steps {
                deleteDir()
                checkout scm
                sh 'git rev-parse HEAD' 

            }
        }

        stage ("Build app image"){
            steps {
                sh 'docker build -t task-manager-app-app:latest .'
            }
        }

        stage ("Build db image"){
            steps {
                sh 'docker build -t task-manager-app-db:latest ./db'
            }
        }

        stage ("Run app containers"){
            steps {
                sh '''
                docker stop task-manager-app-app || true
                docker rm task-manager-app-app || true
                
                docker run -d --name task-manager-app-app -p 5000:5000 task-manager-app-app:latest
                '''

            }
        }

        stage ("Run db containers"){
            steps {
                sh '''
                docker stop task-manager-app-db || true
                docker rm task-manager-app-db || true
                
                docker run -d --name task-manager-app-db -p 3306:3306 task-manager-app-db:latest
                '''

            }
        }

    

    }
}