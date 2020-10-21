# Live Video Analytics (LVA) on Edge with AI Extensibility

## 1. lvaExtension with gRPC interface
Below are instructions that will let you build:

1. Docker container image, **lvaextension**, that consist of a Python 3.8 solution with:
    * gRPC server
    * Inference Engine with gRPC interface
    * Sample ML model with ONNX runtime - Tiny Yolo V3

2. Test application, **client**, that is capable of:
    * creating & managing shared memory space
    * sending sample frames to lvaExtension
      * either embedded into protobuf message
      * or over shared memory space
    * set different media descriptors (define format of data to be sent, i.e. jpeg, bmp, raw etc.)
    * print out the lvaExtension response (inference results)  

### 1.1 Prerequisites
1. [Install Git client](https://git-scm.com/downloads) to clone this repository on your machine.
2. [Install Docker](https://docs.docker.com/engine/install/) on your machine for building AIX Server container image and running it.
3. [Python 3.8 or above](https://www.python.org/) (this version & above has support for specific features) for running AIX-Client test application and Python libraries: gRPC, Open CV and the protobuf by using following commands in the terminal window.
   
```shell
pip install grpcio
pip install opencv-python
pip install protobuf
```

### 1.2. Build LVA Extension Docker container image
1. Clone this sample project repository into a local folder on your PC and switch to the right branch by using following commands in order:  

```shell
git clone https://github.com/mustafakasap/lva_grpc.git
cd lva_grpc
```

After the clone, your local folder structure should show:
```
      .
      ├── client
      │   ├── client.py
      │   ├── media_stream_processor.py
      │   └── sampleframes
      │       └── sample01.png
      ├── contracts
      │   ├── extension.proto
      │   ├── inferencing.proto
      │   └── media.proto
      ├── Dockerfile
      ├── lib
      │   ├── arguments.py
      │   ├── exception_handler.py
      │   ├── extension_pb2_grpc.py
      │   ├── extension_pb2.py
      │   ├── inferencing_pb2.py
      │   ├── media_pb2.py
      │   └── shared_memory.py
      ├── lvaextension
      │   ├── inference_engine.py
      │   ├── model_wrapper.py
      │   └── server.py
      └── readme.md

      5 directories, 18 files
```
2. Open a terminal window, change your current working directory to be the root folder of the local copy of the repository.

3. Build the lvaExtension container image by running the following Docker command in the terminal window:
```
sudo docker build -t lvaextension --file Dockerfile .  
```
In the above command, we use the name "lvaextension" to tag our container image. If you prefer to use another name, you should use the same name in the rest of this document for consistency.

### 1.3. Running and testing
1. Run the lvaextension container using the following Docker command:
```
sudo docker run  --name lvaextension --ipc=host -p 44000:44000 -d  -i lvaextension:latest
```
2. Open a new terminal window and change your current working directory to be **client** folder.  

```
cd client
```  

3. Run the following command to start sending client requests to the aix_server:

```python
python client.py -m -s 127.0.0.1:44000 -l 1 -f sampleframes/sample01.png
```
Parameters in the above command:  
  * **-m**: no value followed with this parameter, just a flag. If it is set, data will be sent over shared memory space. If it is not set, data will be embedded into the message  
  * **-s**: aix server address with port number  
  * **-f**: file name to be used as sample video frame  
  * **-l**: loop count; number of times the sample video frame to be sent to server  

If successful, you will see an output on your screen that looks something like this:
```
[AIXC] [2020-05-13 18:48:49,438] [MainThread  ] [INFO]: gRPC server address: 172.17.0.2:44000
[AIXC] [2020-05-13 18:48:49,438] [MainThread  ] [INFO]: Sample video frame address: sampleframes/sample01.png
[AIXC] [2020-05-13 18:48:49,439] [MainThread  ] [INFO]: How many times to send sample frame to aix server: 1
[AIXC] [2020-05-13 18:48:49,459] [MainThread  ] [INFO]: Shared memory name: /dev/shm/8wy_wguw
[AIXC] [2020-05-13 18:48:49,474] [MainThread  ] [INFO]: [Received] AckNum: 1
[AIXC] [2020-05-13 18:48:49,521] [MainThread  ] [INFO]: [Received] AckNum: 2
[AIXC] [2020-05-13 18:48:49,521] [MainThread  ] [INFO]: sequence_number: 2
ack_sequence_number: 2
media_sample {
  inferences {
    type: ENTITY
    entity {
      tag {
        value: "person"
        confidence: 0.8797584772109985
      }
      box {
        l: 0.6372237801551819
        t: 0.360051691532135
        w: 0.0677151307463646
        h: 0.25818461179733276
      }
    }
  }
  inferences {
    type: ENTITY
    entity {
      tag {
        value: "person"
        confidence: 0.860995888710022
      }
      box {
        l: 0.567323625087738
        t: 0.3887046277523041
        w: 0.05200481414794922
        h: 0.20292653143405914
      }
    }
  }
}

[AIXC] [2020-05-13 18:48:49,521] [MainThread  ] [INFO]: Client finished execution
```

4. Terminate the container using the following Docker commands:  
```shell
sudo docker stop lvaextension && sudo docker rm lvaextension
```
