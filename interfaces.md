


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

Start new pipeline instance. Four sections are supported by default: source, destination, parameters, tags. These sections have special handling based on the [default schema](service/app/modules/schema.py) and/or the schema defined in the pipeline.json file for the requested pipeline.


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
          integer
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
          integer
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
          integer
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
          integer
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
          integer
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
          integer
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
          integer
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