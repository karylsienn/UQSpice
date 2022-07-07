pipeline {
    agent any
    stages {
        stage('check python version') {
            steps {
                sh '/usr/local/opt/python@3.8/bin/python3.8 --version'
            }
        }
        stage('test') {
            steps {
                script {
                    def UQSPICE_HOME = input(
                      id: 'UQSPICE_HOME',
                      message: 'Please provide the UQSpice home directory',
                      parameters: [string(name: 'uqspice_path', description: 'UQSpice path')],
                      ok: 'Submit'
                      ) 
                    sh "/usr/local/opt/python@3.8/bin/python3.8 $UQSPICE_HOME/src/ltspicer/readers.py -r RawReader -f $UQSPICE_HOME/src/test_files/Transient/simple_resistor_stepped_copy.raw"
                }

                
            }    
        }
        
        
        stage('deploy') {
            steps {
                sh "echo 'done'"
            }
        }
    }
}