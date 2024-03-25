pipeline {
  agent any
    stages {
    stage('Python3.7') {
      agent {
        docker {
          image 'python:3.7.16'
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
          image 'python:3.8.16'
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

    stage('Python3.9') {
      agent {
        docker {
          image 'python:3.9.16'
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
          image 'python:3.10.9'
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
          image 'python:3.11.7'
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
          image 'python:3.12.1'
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