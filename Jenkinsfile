pipeline {
  agent any
    stages {
    stage('Python3.9') {
      agent {
        docker {
          image 'python:3.9.20'
          args '-u root:sudo'
        }

      }
      post {
        cleanup {
          cleanWs()
        }

      }
      steps {
        sh 'pip install -r requirements.txt'
        sh 'pip install -U codecov pytest pytest-cov'
        sh 'pytest --cov-report=term-missing --cov=./dart_fss'
        sh 'codecov'
      }
    }

    stage('Python3.10') {
      agent {
        docker {
          image 'python:3.10.17'
          args '-u root:sudo'
        }

      }
      post {
        cleanup {
          cleanWs()
        }

      }
      steps {
        sh 'pip install -r requirements.txt'
        sh 'pip install -U codecov pytest pytest-cov'
        sh 'pytest --cov-report=term-missing --cov=./dart_fss'
        sh 'codecov'
      }
    }

    stage('Python3.11') {
      agent {
        docker {
          image 'python:3.11.12'
          args '-u root:sudo'
        }

      }
      post {
        cleanup {
          cleanWs()
        }

      }
      steps {
        sh 'pip install -r requirements.txt'
        sh 'pip install -U codecov pytest pytest-cov'
        sh 'pytest --cov-report=term-missing --cov=./dart_fss'
        sh 'codecov'
      }
    }
    stage('Python3.12') {
      agent {
        docker {
          image 'python:3.12.11'
          args '-u root:sudo'
        }

      }
      post {
        cleanup {
          cleanWs()
        }

      }
      steps {
        sh 'pip install -r requirements.txt'
        sh 'pip install -U codecov pytest pytest-cov'
        sh 'pytest --runslow --cov-report=term-missing --cov=./dart_fss'
        sh 'codecov'
      }
    }
    stage('Python3.13') {
      agent {
        docker {
          image 'python:3.13.7'
          args '-u root:sudo'
        }

      }
      post {
        cleanup {
          cleanWs()
        }

      }
      steps {
        sh 'pip install -r requirements.txt'
        sh 'pip install -U codecov pytest pytest-cov'
        sh 'pytest --runslow --cov-report=term-missing --cov=./dart_fss'
        sh 'codecov'
      }
    }
  }
  environment {
    DART_API_KEY = credentials('DART_API_KEY')
    CODECOV_TOKEN = credentials('CODECOV_TOKEN')
  }
}