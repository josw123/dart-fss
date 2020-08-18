pipeline {
  agent any
  stages {
    stage('Python3.5') {
      agent {
        docker {
          image 'python:3.5.9'
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

    stage('Python3.6') {
      agent {
        docker {
          image 'python:3.6.11'
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

    stage('Python3.7') {
      agent {
        docker {
          image 'python:3.7.8'
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

    stage('Python3.8') {
      agent {
        docker {
          image 'python:3.8.5'
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

  }
  environment {
    DART_API_KEY = credentials('DART_API_KEY')
    CODECOV_TOKEN = credentials('CODECOV_TOKEN')
  }
}