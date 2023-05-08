Edge Video Analytics Microservice APIs
======================================

Microservice Endpoints
----------------------

The REST API has a default maximum body size of 10 KB, this can be
changed by setting the environment variable MAX_BODY_SIZE in bytes.

.. list-table::
   :widths: 29 43
   :header-rows: 1

   - 

      - Path
      - Description
   - 

      - ```GET`` /models <#get-models>`__
      - Returns the supported models.
   - 

      - ```GET`` /pipelines <#get-pipelines>`__
      - Returns the supported pipelines.
   - 

      - ```GET`` /pipelines/status <#get-pipelinesstatus>`__
      - Returns the status of all pipeline instances.
   - 

      - ```GET``
         /pipelines/{name}/{version} <#get-pipelinesnameversion>`__
      - Returns the pipeline description.
   - 

      - ```POST``
         /pipelines/{name}/{version} <#post-pipelinesnameversion>`__
      - Starts a new pipeline instance.
   - 

      - ```GET`` /pipelines/{instance_id} <#get-pipelinesinstance_id>`__
      - Returns the pipeline instance summary.
   - 

      - ```GET``
         /pipelines/{name}/{version}/{instance_id} <#get-pipelinesnameversioninstance_id>`__
      - Returns the pipeline instance summary.
   - 

      - ```GET``
         /pipelines/status/{instance_id} <#get-pipelinesstatusinstance_id>`__
      - Returns the pipeline instance status.
   - 

      - ```GET``
         /pipelines/{name}/{version}/{instance_id}/status <#get-pipelinesnameversioninstance_idstatus>`__
      - Returns the pipeline instance status.
   - 

      - ```DELETE``
         /pipelines/{instance_id} <#delete-pipelinesinstance_id>`__
      - Stops a running pipeline or cancels a queued pipeline.
   - 

      - ```DELETE``
         /pipelines/{name}/{version}/{instance_id} <#delete-pipelinesnameversioninstance_id>`__
      - Stops a running pipeline or cancels a queued pipeline.

The following endpoints are deprecated and will be removed in a future
release:

 \| Path \| Description \| \|—-\|——\| \| ```GET``
/pipelines/{name}/{version}/{instance_id} <#get-pipelinesnameversioninstance_id>`__
\| Return pipeline instance summary. \| \| ```GET``
/pipelines/{name}/{version}/{instance_id}/status <#get-pipelinesnameversioninstance_idstatus>`__
\| Return pipeline instance status. \| \| ```DELETE``
/pipelines/{name}/{version}/{instance_id} <#delete-pipelinesnameversioninstance_id>`__
\| Stops a running pipeline or cancels a queued pipeline. \|

``GET`` /models
~~~~~~~~~~~~~~~

Returns the supported models.

Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success
                

Example
^^^^^^^

.. code:: json

   [
     {
       "name": "name",
       "description": "description",
       "type": "IntelDLDT",
       "version": 0
     }
   ]


``GET`` /pipelines
~~~~~~~~~~~~~~~~~~

Returns the supported pipelines.

Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success
                

Example
^^^^^^^

.. code:: json

   [
     {
       "description": "description",
       "type": "GStreamer",
       "parameters": {
         "key": {
           "default": ""
         }
       }
     }
   ]


``GET`` /pipelines/status
~~~~~~~~~~~~~~~~~~~~~~~~~

Returns the status of all pipeline instances.

Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success

Example
^^^^^^^

.. code:: json

   [
    {
      "id": 1,
      "state": "COMPLETED",
      "avg_fps": 8.932587737800183,
      "start_time": 1638179813.2005367,
      "elapsed_time": 72.43142008781433,
      "message": "",
      "avg_pipeline_latency": 0.4533823041311556
    },
    {
      "id": 2,
      "state": "RUNNING",
      "avg_fps": 6.366260838099841,
      "start_time": 1638179886.3203313,
      "elapsed_time": 16.493194580078125,
      "message": "",
      "avg_pipeline_latency": 0.6517487730298723
    },
    {
      "id": 3,
      "state": "ERROR",
      "avg_fps": 0,
      "start_time": null,
      "elapsed_time": null,
      "message": "Not Found (404), URL: https://github.com/intel-iot-devkit/sample.mp4, Redirect to: (NULL)"
    }
   ]

``GET`` /pipelines/{name}/{version}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns the pipeline description.

Parameters
^^^^^^^^^^

.. list-table::
   :header-rows: 1

   - 

      - Name
      - Type
      - In
      - Accepted values
   - 

      - name **(required)**
      - string
      - path
      - Any
   - 

      - version **(required)**
      - string
      - path
      - Any

Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success

               

Example
^^^^^^^

.. code:: json

   {
     "description": "description",
     "type": "GStreamer",
     "parameters": {
       "key": {
         "default": ""
       }
     }
   }



``POST`` /pipelines/{name}/{version}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starts a new pipeline instance. Four sections are supported by default:
source, destination, parameters, and tags. These sections have special
handling based on the `default schema </server/schema.py>`__ and/or the
schema defined in the pipeline.json file for the requested pipeline.


Parameters
^^^^^^^^^^

.. list-table::
   :header-rows: 1

   - 

      - Name
      - Type
      - In
      - Accepted values
   - 

      - name **(required)**
      - string
      - path
      - Any
   - 

      - version **(required)**
      - string
      - path
      - Any


Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success

Example
^^^^^^^

.. code:: json

   {
     "source": {
       "type": "uri",
       "uri": "file:///root/video-examples/example.mp4"
     },
     "destination":{},
     "parameters": {},
     "tags": {}
   }


``DELETE`` /pipelines/{instance_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stops the pipeline instance.

Parameters
^^^^^^^^^^

.. list-table::
   :header-rows: 1

   - 

      - Name
      - Type
      - In
      - Accepted values
   - 

      - instance_id **(required)**
      - string
      - path
      - Any

Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success


``DELETE`` /pipelines/{name}/{version}/{instance_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Stops the pipeline instance.


Parameters
^^^^^^^^^^

.. list-table::
   :header-rows: 1

   - 

      - Name
      - Type
      - In
      - Accepted values
   - 

      - name **(required)**
      - string
      - path
      - Any
   - 

      - version **(required)**
      - string
      - path
      - Any
   - 

      - instance_id **(required)**
      - string
      - path
      - Any

Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success


``GET`` /pipelines/{name}/{version}/{instance_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns the pipeline instance summary.


Parameters
^^^^^^^^^^

.. list-table::
   :header-rows: 1

   - 

      - Name
      - Type
      - In
      - Accepted values
   - 

      - name **(required)**
      - string
      - path
      - Any
   - 

      - version **(required)**
      - string
      - path
      - Any
   - 

      - instance_id **(required)**
      - string
      - path
      - Any


Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success
                

Example
^^^^^^^

.. code:: json

   {
     "request": {
       "destination": {},
       "source": {},
       "parameters": {},
       "tags": {}
     },
     "id": 0,
     "type": "type"
   }

``GET`` /pipelines/{instance_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns the pipeline instance summary.


Parameters
^^^^^^^^^^


.. list-table::
   :header-rows: 1

   - 

      - Name
      - Type
      - In
      - Accepted values
   - 

      - instance_id **(required)**
      - string
      - path
      - Any


Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success
                

Example
^^^^^^^

.. code:: json

   {
     "id": 0,
     "launch_command": "",
     "name": "",
     "request": {
       "destination": {},
       "source": {},
       "parameters": {},
       "tags": {}
     },
     "type": "type",
     "version": ""
   }


``GET`` /pipelines/status/{instance_id}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns the pipeline instance status.

Parameters
^^^^^^^^^^

.. list-table::
   :header-rows: 1

   - 

      - Name
      - Type
      - In
      - Accepted values
   - 

      - instance_id **(required)**
      - string
      - path
      - Any


Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success
                

Example
^^^^^^^

.. code:: json

   {
     "avg_fps": 12.077234499118983,
     "elapsed_time": 12.999657154083252,
     "id": 1,
     "name": "object_detection",
     "start_time": 1640156425.2014737,
     "state": "RUNNING",
     "message": "",
     "version": "person_vehicle_bike"
   }


``GET`` /pipelines/{name}/{version}/{instance_id}/status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns the pipeline instance status.

Parameters
^^^^^^^^^^

.. list-table::
   :header-rows: 1

   - 

      - Name
      - Type
      - In
      - Accepted values
   - 

      - name **(required)**
      - string
      - path
      - Any
   - 

      - version **(required)**
      - string
      - path
      - Any
   - 

      - instance_id **(required)**
      - string
      - path
      - Any


Response
^^^^^^^^

.. list-table::
   :widths: 20 80
   :header-rows: 1

   - 

      - Code
      - Description
   - 

      - 200
      - Success
               

Example
^^^^^^^

.. code:: json

   {
     "start_time": 1,
     "elapsed_time": 5,
     "id": 0,
     "state": "RUNNING",
     "message": "",
     "avg_fps": 6.027456183070403
   }
