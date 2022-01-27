## Microservice Endpoints

| Path | Description |
|----|------|
| [`GET` /models](#get-models) | Return supported models. |
| [`GET` /pipelines](#get-pipelines) | Return supported pipelines. |
| [`GET` /pipelines/status](#get-pipelinesstatus) | Return status of all pipeline instances. |
| [`GET` /pipelines/{name}/{version}](#get-pipelinesnameversion)  | Return pipeline description.|
| [`POST` /pipelines/{name}/{version}](#post-pipelinesnameversion) | Start new pipeline instance. |
| [`GET` /pipelines/{instance_id}](#get-pipelinesinstance_id) | Return pipeline instance summary. |
| [`GET` /pipelines/{name}/{version}/{instance_id}](#get-pipelinesnameversioninstance_id) | Return pipeline instance summary. |
| [`GET` /pipelines/status/{instance_id}](#get-pipelinesstatusinstance_id) | Return pipeline instance status. |
| [`GET` /pipelines/{name}/{version}/{instance_id}/status](#get-pipelinesnameversioninstance_idstatus) | Return pipeline instance status. |
| [`DELETE` /pipelines/{instance_id}](#delete-pipelinesinstance_id) | Stops a running pipeline or cancels a queued pipeline. |
| [`DELETE` /pipelines/{name}/{version}/{instance_id}](#delete-pipelinesnameversioninstance_id) | Stops a running pipeline or cancels a queued pipeline. |

The following endpoints are deprecated and will be removed by v1.0.
| Path | Description |
|----|------|
| [`GET` /pipelines/{name}/{version}/{instance_id}](#get-pipelinesnameversioninstance_id) | Return pipeline instance summary. |
| [`GET` /pipelines/{name}/{version}/{instance_id}/status](#get-pipelinesnameversioninstance_idstatus) | Return pipeline instance status. |
| [`DELETE` /pipelines/{name}/{version}/{instance_id}](#delete-pipelinesnameversioninstance_id) | Stops a running pipeline or cancels a queued pipeline. |

### `GET` /models
<a id="op-get-models" />

Return supported models

#### Responses


#####   200 - Success

###### application/json

##### Example

```json
[
  {
    "name": "name",
    "description": "description",
    "type": "IntelDLDT",
    "version": 0
  }
]
```

</div>

### `GET` /pipelines
<a id="op-get-pipelines" />

Return supported pipelines


#### Responses

#####   200 - Success
###### application/json
##### Example _(generated)_

```json
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
```

</div>

 ### `GET` /pipelines/status
 <a id="op-get-pipelines-status" />

 Return status of all pipeline instances.


 #### Responses

 #####   200 - Success
 ###### application/json
 ##### Example _(generated)_

 ```json
[
  {
    "id": 1,
    "state": "COMPLETED",
    "avg_fps": 8.932587737800183,
    "start_time": 1638179813.2005367,
    "elapsed_time": 72.43142008781433,
    "avg_pipeline_latency": 0.4533823041311556
  },
  {
    "id": 2,
    "state": "RUNNING",
    "avg_fps": 6.366260838099841,
    "start_time": 1638179886.3203313,
    "elapsed_time": 16.493194580078125,
    "avg_pipeline_latency": 0.6517487730298723
  },
  {
    "id": 3,
    "state": "ERROR",
    "avg_fps": 0,
    "start_time": null,
    "elapsed_time": null
  }
]
 ```

 </div>

### `GET` /pipelines/{name}/{version}
<a id="op-get-pipelines-name-version" />

Return pipeline description.

#### Path parameters

##### &#9655; name

<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>name  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>


##### &#9655; version



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>version  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>


#### Responses


#####   200 - Success

###### application/json

##### Example
```json
{
  "description": "description",
  "type": "GStreamer",
  "parameters": {
    "key": {
      "default": ""
    }
  }
}
```

</div>

### `POST` /pipelines/{name}/{version}
<a id="op-post-pipelines-name-version" />

Start new pipeline instance. Four sections are supported by default: source, destination, parameters, and tags.
These sections have special handling based on the [default schema](/vaserving/schema.py) and/or the schema
defined in the pipeline.json file for the requested pipeline.


#### Path parameters

##### &#9655; name



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>name  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>


##### &#9655; version



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>version  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>






#### Request body
###### application/json

##### Example


```json
{
  "source": {
    "type": "uri",
    "uri": "file:///root/video-examples/example.mp4"
  },
  "destination":{},
  "parameters": {},
  "tags": {}
}
```

#### Responses

#####   200 - Success

</div>

### `DELETE` /pipelines/{instance_id}
<a id="op-delete-pipelines-instance-id" />

Stop pipeline instance.


#### Path parameters

##### &#9655; instance_id



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>instance_id  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>



#### Responses

#####   200 - Success

</div>

### `DELETE` /pipelines/{name}/{version}/{instance_id}
<a id="op-delete-pipelines-name-version-instance-id" />

Stop pipeline instance.


#### Path parameters

##### &#9655; name


<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>name  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>


##### &#9655; version



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>version  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>


##### &#9655; instance_id



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>instance_id  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>



#### Responses

#####   200 - Success

</div>

### `GET` /pipelines/{name}/{version}/{instance_id}
<a id="op-get-pipelines-name-version-instance-id" />

Return pipeline instance summary.


#### Path parameters

##### &#9655; name



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>name  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>

##### &#9655; version



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>version  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>


##### &#9655; instance_id



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>instance_id  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>

#### Responses

#####   200 - Success

###### application/json

##### Example
```json
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
```

### `GET` /pipelines/{instance_id}
<a id="op-get-pipelines-instance-id" />

Return pipeline instance summary.


#### Path parameters

##### &#9655; instance_id



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>instance_id  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>

#### Responses

#####   200 - Success

###### application/json

##### Example
```json
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
```

</div>

### `GET` /pipelines/status/{instance_id}
<a id="op-get-pipelines-status-instance-id" />

Return pipeline instance status.


#### Path parameters

##### &#9655; instance_id



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>instance_id  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>

#### Responses


#####   200 - Success

###### application/json

##### Example
```json
{
  "avg_fps": 12.077234499118983,
  "elapsed_time": 12.999657154083252,
  "id": 1,
  "name": "object_detection",
  "start_time": 1640156425.2014737,
  "state": "RUNNING",
  "version": "person_vehicle_bike"
}
```

</div>


### `GET` /pipelines/{name}/{version}/{instance_id}/status
<a id="op-get-pipelines-name-version-instance-id-status" />

Return pipeline instance status.


#### Path parameters

##### &#9655; name



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>name  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>


##### &#9655; version



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>version  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>


##### &#9655; instance_id



<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Type</th>
      <th>In</th>
      <th>Accepted values</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>instance_id  <strong>(required)</strong></td>
        <td>
          string
        </td>
        <td>path</td>
        <td><em>Any</em></td>
      </tr>
  </tbody>
</table>

#### Responses


#####   200 - Success

###### application/json

##### Example
```json
{
  "start_time": 1,
  "elapsed_time": 5,
  "id": 0,
  "state": "RUNNING",
  "avg_fps": 6.027456183070403
}
```

</div>
